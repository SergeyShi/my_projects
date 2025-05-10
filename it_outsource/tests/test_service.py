from odoo.tests.common import TransactionCase

class TestService(TransactionCase):
    def setUp(self):
        super(TestService, self).setUp()
        self.Service = self.env['it.outsource.service']
        
    def test_create_service(self):
        service = self.Service.create({
            'name': 'Test Service',
            'code': 'TEST',
            'monthly_price': 50,
        })
        self.assertEqual(service.name, 'Test Service')
        self.assertEqual(service.code, 'TEST')
        self.assertEqual(service.monthly_price, 50)
        
    def test_unique_code(self):
        self.Service.create({
            'name': 'Service 1',
            'code': 'DUPLICATE',
            'monthly_price': 50,
        })
        with self.assertRaises(Exception):
            self.Service.create({
                'name': 'Service 2',
                'code': 'DUPLICATE',
                'monthly_price': 100,
            })
