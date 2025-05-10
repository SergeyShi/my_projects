from odoo.tests.common import TransactionCase
from datetime import date, timedelta

class TestInvoice(TransactionCase):
    def setUp(self):
        super(TestInvoice, self).setUp()
        self.Invoice = self.env['it.outsource.invoice']
        self.Contract = self.env['it.outsource.contract']
        self.partner = self.env.ref('base.res_partner_1')
        self.server = self.env['it.outsource.server'].create({
            'name': 'Test Server',
            'monthly_price': 100,
        })
        
    def test_invoice_creation(self):
        contract = self.Contract.create({
            'partner_id': self.partner.id,
            'start_date': date.today(),
            'server_ids': [(6, 0, [self.server.id])],
            'state': 'active',
        })
        invoice = self.Invoice.create({
            'contract_id': contract.id,
        })
        self.assertEqual(invoice.amount, 100)
        self.assertEqual(invoice.due_date, invoice.date + timedelta(days=30))
        
    def test_invoice_states(self):
        contract = self.Contract.create({
            'partner_id': self.partner.id,
            'start_date': date.today(),
            'server_ids': [(6, 0, [self.server.id])],
            'state': 'active',
        })
        invoice = self.Invoice.create({
            'contract_id': contract.id,
        })
        invoice.action_send()
        self.assertEqual(invoice.state, 'sent')
        invoice.action_paid()
        self.assertEqual(invoice.state, 'paid')
