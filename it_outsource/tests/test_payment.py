from datetime import datetime, timedelta
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestPayment(TransactionCase):
    """Test suite for the Payment functionality.
    This class contains test cases for the payment module, which is responsible
    for managing payments in the IT outsourcing system. The tests cover various
    aspects including creation, validation, workflow states, and business logic.
    Attributes:
        partner (res.partner): Test partner record
        server (it_outsource.product): Test server product record
        contract (it_outsource.contract): Test contract record
        invoice (it_outsource.invoice): Test invoice record
    """
    @classmethod
    def setUpClass(cls):
        """Set up test data for all test methods.
        Creates the necessary test records:
        - A test partner
        - A test server product
        - A test contract
        - A test invoice
        """
        super(TestPayment, cls).setUpClass()
        # Create test partner
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Client',
            'email': 'test@example.com',
            'phone': '+380501234567',
        })
        # Create test products
        cls.server = cls.env['it_outsource.product'].create({
            'name': 'Test Server',
            'product_type': 'server',
            'price': 1000.0,
            'cpu_count': 4,
            'ram_gb': 16,
            'disk_space_gb': 500,
        })
        # Create test contract
        cls.contract = cls.env['it_outsource.contract'].create({
            'partner_id': cls.partner.id,
            'start_date': datetime.now(),
            'end_date': datetime.now() + timedelta(days=365),
            'product_ids': [(4, cls.server.id)],
        })
        cls.contract.action_confirm()
        # Create test invoice
        cls.invoice = cls.env['it_outsource.invoice'].create({
            'partner_id': cls.partner.id,
            'contract_id': cls.contract.id,
            'date': datetime.now(),
            'due_date': datetime.now() + timedelta(days=30),
            'line_ids': [(0, 0, {
                'product_id': cls.server.id,
                'quantity': 1,
                'price_unit': cls.server.price,
            })],
        })
        cls.invoice.action_send()

    def test_01_create_payment(self):
        """Test basic payment creation.
        Verifies that:
        - Payment can be created with basic required fields
        - Payment is in draft state after creation
        - Partner is correctly linked
        """
        payment = self.env['it_outsource.payment'].create({
            'invoice_id': self.invoice.id,
            'amount': 1000.0,
            'payment_method': 'bank',
            'date': datetime.now(),
        })
        self.assertTrue(payment, "Payment should be created")
        self.assertEqual(payment.state,
                         'draft',
                         "Payment should be in draft state")
        self.assertEqual(payment.partner_id, self.partner,
                         "Payment should be linked to the correct partner")

    def test_02_payment_validation(self):
        """Test payment validation workflow.
        Verifies that:
        - Payment can be confirmed
        - Payment state changes to confirmed
        - Payment cannot be cancelled without reason
        """
        payment = self.env['it_outsource.payment'].create({
            'invoice_id': self.invoice.id,
            'amount': 1000.0,
            'payment_method': 'bank',
            'date': datetime.now(),
        })
        payment.action_confirm()
        self.assertEqual(payment.state,
                         'confirmed',
                         "Payment should be confirmed")
        # Test that confirmed payment can't be cancelled without reason
        with self.assertRaises(ValidationError):
            payment.action_cancel()

    def test_03_payment_amount_validation(self):
        """Test payment amount validation.
        Verifies that:
        - Payment amount cannot exceed invoice amount
        - Payment amount cannot be negative
        - Appropriate validation errors are raised
        """
        # Test payment amount greater than invoice amount
        with self.assertRaises(ValidationError):
            self.env['it_outsource.payment'].create({
                'invoice_id': self.invoice.id,
                'amount': 2000.0,
                'payment_method': 'bank',
                'date': datetime.now(),
            })
        # Test negative payment amount
        with self.assertRaises(ValidationError):
            self.env['it_outsource.payment'].create({
                'invoice_id': self.invoice.id,
                'amount': -1000.0,
                'payment_method': 'bank',
                'date': datetime.now(),
            })

    def test_04_payment_cancellation(self):
        """Test payment cancellation with reason.
        Verifies that:
        - Payment can be cancelled with a reason
        - Payment state changes to cancelled
        """
        payment = self.env['it_outsource.payment'].create({
            'invoice_id': self.invoice.id,
            'amount': 1000.0,
            'payment_method': 'bank',
            'date': datetime.now(),
        })
        payment.write({'cancellation_reason': 'Test cancellation'})
        payment.action_cancel()
        self.assertEqual(payment.state, 'cancelled', "Payment should be cancelled")

    def test_05_payment_method_validation(self):
        """Test payment method validation.
        Verifies that:
        - Only valid payment methods are accepted
        - Appropriate validation error is raised for invalid method
        """
        # Test invalid payment method
        with self.assertRaises(ValidationError):
            self.env['it_outsource.payment'].create({
                'invoice_id': self.invoice.id,
                'amount': 1000.0,
                'payment_method': 'invalid_method',
                'date': datetime.now(),
            })

    def test_06_payment_date_validation(self):
        """Test payment date validation.
        Verifies that:
        - Payment date cannot be in the future
        - Appropriate validation error is raised
        """
        # Test future payment date
        with self.assertRaises(ValidationError):
            self.env['it_outsource.payment'].create({
                'invoice_id': self.invoice.id,
                'amount': 1000.0,
                'payment_method': 'bank',
                'date': datetime.now() + timedelta(days=1),
            })

    def test_07_multiple_payments(self):
        """Test multiple payments for one invoice.
        Verifies that:
        - Multiple payments can be recorded for one invoice
        - Total paid amount is calculated correctly
        - Invoice state changes to paid after full payment
        """
        # Create first payment
        payment1 = self.env['it_outsource.payment'].create({
            'invoice_id': self.invoice.id,
            'amount': 500.0,
            'payment_method': 'bank',
            'date': datetime.now(),
        })
        payment1.action_confirm()
        # Create second payment
        payment2 = self.env['it_outsource.payment'].create({
            'invoice_id': self.invoice.id,
            'amount': 500.0,
            'payment_method': 'cash',
            'date': datetime.now(),
        })
        payment2.action_confirm()
        self.assertEqual(self.invoice.paid_amount,
                         second=1000.0,
                         msg="Total paid amount should be correct")
        self.assertEqual(self.invoice.state,
                         second='paid',
                         msg="Invoice should be paid after full payment")

    def test_08_payment_notes(self):
        """Test payment notes functionality.
        Verifies that:
        - Notes can be added to the payment
        - Notes are saved correctly
        """
        test_notes = "Test payment notes"
        payment = self.env['it_outsource.payment'].create({
            'invoice_id': self.invoice.id,
            'amount': 1000.0,
            'payment_method': 'bank',
            'date': datetime.now(),
            'notes': test_notes,
        })
        self.assertEqual(payment.notes, test_notes,
                         "Payment notes should be saved correctly")
