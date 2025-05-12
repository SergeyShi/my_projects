from datetime import datetime, timedelta
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestContract(TransactionCase):
    """Test suite for the Contract functionality.
    This class contains test cases for the contract module, which is responsible
    for managing IT outsourcing contracts. The tests cover various aspects
    including creation, validation, workflow states, and business logic.
    Attributes:
        partner (res.partner): Test partner record
        server (it_outsource.product): Test server product record
        service (it_outsource.product): Test service product record
    """

    @classmethod
    def setUpClass(cls):
        """Set up test data for all test methods.
        Creates the necessary test records:
        - A test partner
        - Two test products (server and service)
        """
        super(TestContract, cls).setUpClass()
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

    def test_01_create_contract(self):
        """Test basic contract creation.
        Verifies that:
        - Contract can be created with basic required fields
        - Contract is in draft state after creation
        - Products are correctly linked to the contract
        """
        contract = self.env['it_outsource.contract'].create({
            'partner_id': self.partner.id,
            'start_date': datetime.now(),
            'end_date': datetime.now() + timedelta(days=365),
            'product_ids': [(4, self.server.id), (4, self.service.id)],
        })
        self.assertTrue(contract, "Contract should be created")
        self.assertEqual(contract.state,
                         second='draft', msg="Contract should be in draft state")
        self.assertEqual(len(contract.product_ids),
                         second=2, msg="Contract should have 2 products")

    def test_02_contract_validation(self):
        """Test contract validation workflow.
        Verifies that:
        - Contract can be confirmed
        - Contract state changes to active after confirmation
        - Contract cannot be cancelled without reason
        """
        contract = self.env['it_outsource.contract'].create({
            'partner_id': self.partner.id,
            'start_date': datetime.now(),
            'end_date': datetime.now() + timedelta(days=365),
            'product_ids': [(4, self.server.id)],
        })
        contract.action_confirm()
        self.assertEqual(contract.state,
                         second='active', msg="Contract should be active after confirmation")
        # Test that active contract can't be cancelled without reason
        with self.assertRaises(ValidationError):
            contract.action_cancel()

    def test_03_contract_cancellation(self):
        """Test contract cancellation with reason.
        Verifies that:
        - Contract can be cancelled with a reason
        - Contract state changes to cancelled
        """
        contract = self.env['it_outsource.contract'].create({
            'partner_id': self.partner.id,
            'start_date': datetime.now(),
            'end_date': datetime.now() + timedelta(days=365),
            'product_ids': [(4, self.server.id)],
        })
        contract.action_confirm()
        contract.write({'cancellation_reason': 'Test cancellation'})
        contract.action_cancel()
        self.assertEqual(contract.state, 'cancelled', "Contract should be cancelled")

    def test_04_contract_dates_validation(self):
        """Test contract dates validation.
        Verifies that:
        - End date cannot be before start date
        - Start date cannot be in the past
        - Appropriate validation errors are raised
        """
        # Test end date before start date
        with self.assertRaises(ValidationError):
            self.env['it_outsource.contract'].create({
                'partner_id': self.partner.id,
                'start_date': datetime.now(),
                'end_date': datetime.now() - timedelta(days=1),
            })
        # Test start date in the past
        with self.assertRaises(ValidationError):
            self.env['it_outsource.contract'].create({
                'partner_id': self.partner.id,
                'start_date': datetime.now() - timedelta(days=1),
                'end_date': datetime.now() + timedelta(days=365),
            })

    def test_05_contract_products_validation(self):
        """Test contract products validation.
        Verifies that:
        - Contract cannot be created without products
        - Appropriate validation error is raised
        """
        # Test contract without products
        with self.assertRaises(ValidationError):
            self.env['it_outsource.contract'].create({
                'partner_id': self.partner.id,
                'start_date': datetime.now(),
                'end_date': datetime.now() + timedelta(days=365),
            })

    def test_06_contract_expiration(self):
        """Test contract expiration.
        Verifies that:
        - Contract state changes to expired when end date is passed
        - Contract is automatically marked as expired
        """
        contract = self.env['it_outsource.contract'].create({
            'partner_id': self.partner.id,
            'start_date': datetime.now() - timedelta(days=366),
            'end_date': datetime.now() - timedelta(days=1),
            'product_ids': [(4, self.server.id)],
        })
        contract.action_confirm()
        self.assertEqual(contract.state,
                         second='expired',
                         msg="Contract should be expired")

    def test_07_contract_monthly_total(self):
        """Test contract monthly total calculation.
        Verifies that:
        - Monthly total is calculated correctly
        - Total includes all products' prices
        """
        contract = self.env['it_outsource.contract'].create({
            'partner_id': self.partner.id,
            'start_date': datetime.now(),
            'end_date': datetime.now() + timedelta(days=365),
            'product_ids': [(4, self.server.id), (4, self.service.id)],
        })
        expected_total = self.server.price + self.service.price
        self.assertEqual(contract.monthly_total, expected_total,
                         msg="Monthly total should be calculated correctly")

    def test_08_contract_notes(self):
        """Test contract notes functionality.
        Verifies that:
        - Notes can be added to the contract
        - Notes are saved correctly
        """
        test_notes = "Test contract notes"
        contract = self.env['it_outsource.contract'].create({
            'partner_id': self.partner.id,
            'start_date': datetime.now(),
            'end_date': datetime.now() + timedelta(days=365),
            'product_ids': [(4, self.server.id)],
            'notes': test_notes,
        })
        self.assertEqual(contract.notes, test_notes,
                         msg="Contract notes should be saved correctly")
