from odoo.tests.common import TransactionCase

class TestServer(TransactionCase):
    def setUp(self):
        super(TestServer, self).setUp()
        self.Server = self.env['it.outsource.server']
        
    def test_create_server(self):
        server = self.Server.create({
            'name': 'Test Server',
            'hostname': 'test-server',
            'monthly_price': 100,
        })
        self.assertEqual(server.name, 'Test Server')
        self.assertEqual(server.hostname, 'test-server')
        self.assertEqual(server.monthly_price, 100)
        
    def test_unique_hostname(self):
        self.Server.create({
            'name': 'Server 1',
            'hostname': 'duplicate',
            'monthly_price': 100,
        })
        with self.assertRaises(Exception):
            self.Server.create({
                'name': 'Server 2',
                'hostname': 'duplicate',
                'monthly_price': 200,
            })
