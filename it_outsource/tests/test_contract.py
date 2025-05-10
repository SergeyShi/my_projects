from odoo.tests.common import TransactionCase
from datetime import date, timedelta

class TestContract(TransactionCase):
    def setUp(self):
        super(TestContract, self).setUp()
        self.Contract = self.env['it.outsource.contract']
        self.partner = self.env.ref('base.res_partner_1')
        self.server = self.env['it.outsource.server'].create({
            'name': 'Test Server',
            'monthly_price': 100,
        })
        self.service = self.env['it.outsource.service'].create({
            'name': 'Test Service',
            'monthly_price': 50,
        })
        
    def test_create_contract(self):
        contract = self.Contract.create({
            'partner_id': self.partner.id,
            'start_date': date.today(),
            'server_ids': [(6, 0, [self.server.id])],
            'service_ids': [(6, 0, [self.service.id])],
        })
        self.assertEqual(contract.monthly_total, 150)
        
    def test_state_changes(self):
        contract = self.Contract.create({
            'partner_id': self.partner.id,
            'start_date': date.today(),
            'server_ids': [(6, 0, [self.server.id])],
        })
        contract.action_activate()
        self.assertEqual(contract.state, 'active')
        contract.action_expire()
        self.assertEqual(contract.state, 'expired')
