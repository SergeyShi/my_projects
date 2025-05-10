from odoo.tests.common import TransactionCase
from datetime import date

class TestPayment(TransactionCase):
    def setUp(self):
        super(TestPayment, self).setUp()
        self.Payment = self.env['it.outsource.payment']
        self.Invoice = self.env['it.outsource.invoice']
        self.Contract = self.env['it.outsource.contract']
        self.partner = self.env.ref('base.res_partner_1')
        self.server = self.env['it.outsource.server'].create({
            'name': 'Test Server',
            'monthly_price': 100,
        })
        
    def test_payment_creation(self):
        contract = self.Contract.create({
            'partner_id': self.partner.id,
            'start_date': date.today(),
            'server_ids': [(6, 0, [self.server.id])],
            'state': 'active',
        })
        invoice = self.Invoice.create({
            'contract_id': contract.id,
        })
        payment = self.Payment.create({
            'invoice_id': invoice.id,
            'amount': 50,
            'payment_method': 'bank',
        })
        self.assertEqual(payment.amount, 50)
        self.assertEqual(invoice.paid_amount, 50)
        self.assertEqual(invoice.residual, 50)
        
    def test_payment_validation(self):
        contract = self.Contract.create({
            'partner_id': self.partner.id,
            'start_date': date.today(),
            'server_ids': [(6, 0, [self.server.id])],
            'state': 'active',
        })
        invoice = self.Invoice.create({
            'contract_id': contract.id,
        })
        with self.assertRaises(Exception):
            self.Payment.create({
                'invoice_id': invoice.id,
                'amount': 150,
                'payment_method': 'bank',
            })
