from datetime import datetime, timedelta
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestInvoice(TransactionCase):
    """Test suite for the Invoice functionality.
    This class contains test cases for the invoice module, which is responsible
    for managing invoices in the IT outsourcing system. The tests cover various
    aspects including creation, validation, payment processing, and business logic.
    Attributes:
        partner (res.partner): Test partner record
        server (it_outsource.product): Test server product record
        service (it_outsource.product): Test service product record
        contract (it_outsource.contract): Test contract record
    """

    @classmethod
    def setUpClass(cls):
        """Set up test data for all test methods.
        Creates the necessary test records:
        - A test partner
        - Two test products (server and service)
        - A test contract linking the partner and products
        """
        super(TestInvoice, cls).setUpClass()
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
        cls.service = cls.env['it_outsource.product'].create({
            'name': 'Test Service',
            'product_type': 'service',
            'price': 500.0,
        })
        # Create test contract
        cls.contract = cls.env['it_outsource.contract'].create({
            'partner_id': cls.partner.id,
            'start_date': datetime.now(),
            'end_date': datetime.now() + timedelta(days=365),
            'product_ids': [(4, cls.server.id), (4, cls.service.id)],
        })
        cls.contract.action_confirm()

    def test_01_create_invoice(self):
        """Test basic invoice creation.
        Verifies that:
        - Invoice can be created with basic required fields
        - Invoice is in draft state after creation
        - Lines are correctly created
        - Total amount is calculated correctly
        """
        invoice = self.env['it_outsource.invoice'].create({
            'partner_id': self.partner.id,
            'contract_id': self.contract.id,
            'date': datetime.now(),
            'due_date': datetime.now() + timedelta(days=30),
            'line_ids': [
                (0, 0, {
                    'product_id': self.server.id,
                    'quantity': 1,
                    'price_unit': self.server.price,
                }),
                (0, 0, {
                    'product_id': self.service.id,
                    'quantity': 1,
                    'price_unit': self.service.price,
                }),
            ],
        })
        self.assertTrue(invoice, "Invoice should be created")
        self.assertEqual(invoice.state,
                         'draft',
                         "Invoice should be in draft state")
        self.assertEqual(len(invoice.line_ids),
                         2,
                         "Invoice should have 2 lines")
        self.assertEqual(invoice.amount,
                         1500.0,
                         "Invoice amount should be calculated correctly")

    def test_02_invoice_validation(self):
        """Test invoice validation workflow.
        Verifies that:
        - Invoice can be sent
        - Invoice state changes to sent
        - Invoice cannot be cancelled without reason
        """
        invoice = self.env['it_outsource.invoice'].create({
            'partner_id': self.partner.id,
            'contract_id': self.contract.id,
            'date': datetime.now(),
            'due_date': datetime.now() + timedelta(days=30),
            'line_ids': [(0, 0, {
                'product_id': self.server.id,
                'quantity': 1,
                'price_unit': self.server.price,
            })],
        })
        invoice.action_send()
        self.assertEqual(invoice.state, 'sent', "Invoice should be sent")
        # Test that sent invoice can't be cancelled without reason
        with self.assertRaises(ValidationError):
            invoice.action_cancel()

    def test_03_invoice_payment(self):
        """Test invoice payment workflow.
        Verifies that:
        - Partial payment can be recorded
        - Full payment can be recorded
        - Invoice state changes correctly based on payment status
        - Paid amount is calculated correctly
        """
        invoice = self.env['it_outsource.invoice'].create({
            'partner_id': self.partner.id,
            'contract_id': self.contract.id,
            'date': datetime.now(),
            'due_date': datetime.now() + timedelta(days=30),
            'line_ids': [(0, 0, {
                'product_id': self.server.id,
                'quantity': 1,
                'price_unit': self.server.price,
            })],
        })
        invoice.action_send()
        # Create partial payment
        payment = self.env['it_outsource.payment'].create({
            'invoice_id': invoice.id,
            'amount': 500.0,
            'payment_method': 'bank',
            'date': datetime.now(),
        })
        payment.action_confirm()
        self.assertEqual(invoice.paid_amount,
                         500.0,
                         "Partial payment should be recorded")
        self.assertEqual(invoice.state,
                         'sent',
                         "Invoice should still be sent with partial payment")

        payment = self.env['it_outsource.payment'].create({
            'invoice_id': invoice.id,
            'amount': 500.0,
            'payment_method': 'bank',
            'date': datetime.now(),
        })
        payment.action_confirm()
        self.assertEqual(invoice.state, 'paid', "Invoice should be paid after full payment")

    def test_04_invoice_cancellation(self):
        """Test invoice cancellation with reason.
        Verifies that:
        - Invoice can be cancelled with a reason
        - Invoice state changes to cancelled
        """
        invoice = self.env['it_outsource.invoice'].create({
            'partner_id': self.partner.id,
            'contract_id': self.contract.id,
            'date': datetime.now(),
            'due_date': datetime.now() + timedelta(days=30),
            'line_ids': [(0, 0, {
                'product_id': self.server.id,
                'quantity': 1,
                'price_unit': self.server.price,
            })],
        })
        invoice.write({'cancellation_reason': 'Test cancellation'})
        invoice.action_cancel()
        self.assertEqual(invoice.state,
                         'cancelled',
                         "Invoice should be cancelled")

    def test_05_invoice_dates_validation(self):
        """Test invoice dates validation.
        Verifies that:
        - Due date cannot be before invoice date
        - Appropriate validation error is raised
        """
        # Test due date before invoice date
        with self.assertRaises(ValidationError):
            self.env['it_outsource.invoice'].create({
                'partner_id': self.partner.id,
                'contract_id': self.contract.id,
                'date': datetime.now(),
                'due_date': datetime.now() - timedelta(days=1),
                'line_ids': [(0, 0, {
                    'product_id': self.server.id,
                    'quantity': 1,
                    'price_unit': self.server.price,
                })],
            })

    def test_06_invoice_lines_validation(self):
        """Test invoice lines validation.
        Verifies that:
        - Invoice cannot be created without lines
        - Appropriate validation error is raised
        """
        # Test invoice without lines
        with self.assertRaises(ValidationError):
            self.env['it_outsource.invoice'].create({
                'partner_id': self.partner.id,
                'contract_id': self.contract.id,
                'date': datetime.now(),
                'due_date': datetime.now() + timedelta(days=30),
            })

    def test_07_invoice_amount_calculation(self):
        """Test invoice amount calculation.
        Verifies that:
        - Total amount is calculated correctly for multiple lines
        - Different quantities and prices are handled correctly
        """
        invoice = self.env['it_outsource.invoice'].create({
            'partner_id': self.partner.id,
            'contract_id': self.contract.id,
            'date': datetime.now(),
            'due_date': datetime.now() + timedelta(days=30),
            'line_ids': [
                (0, 0, {
                    'product_id': self.server.id,
                    'quantity': 2,
                    'price_unit': self.server.price,
                }),
                (0, 0, {
                    'product_id': self.service.id,
                    'quantity': 3,
                    'price_unit': self.service.price,
                }),
            ],
        })
        expected_amount = (2 * self.server.price) + (3 * self.service.price)
        self.assertEqual(invoice.amount, expected_amount, "Invoice amount should be calculated correctly")

    def test_08_invoice_residual_amount(self):
        """Test invoice residual amount calculation.
        Verifies that:
        - Residual amount is calculated correctly after partial payment
        - Paid amount is tracked correctly
        """
        invoice = self.env['it_outsource.invoice'].create({
            'partner_id': self.partner.id,
            'contract_id': self.contract.id,
            'date': datetime.now(),
            'due_date': datetime.now() + timedelta(days=30),
            'line_ids': [(0, 0, {
                'product_id': self.server.id,
                'quantity': 1,
                'price_unit': self.server.price,
            })],
        })
        invoice.action_send()

        payment = self.env['it_outsource.payment'].create({
            'invoice_id': invoice.id,
            'amount': 500.0,
            'payment_method': 'bank',
            'date': datetime.now(),
        })
        payment.action_confirm()
        self.assertEqual(invoice.residual,
                         500.0,
                         "Residual amount should be calculated correctly")
