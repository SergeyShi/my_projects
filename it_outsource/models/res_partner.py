from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # rental_server_ids = fields.One2many('server.rental.server', 'partner_id', string='Rental Servers')
    # rental_service_ids = fields.One2many('server.rental.service', 'partner_id', string='Rental Services')
    rental_contract_ids = fields.One2many('it.outsource.contract', 'partner_id', string='Rental Contracts')
    # rental_invoice_ids = fields.One2many('server.rental.invoice', 'partner_id', string='Rental Invoices')
    # rental_payment_ids = fields.One2many('server.rental.payment', 'partner_id', string='Rental Payments')
    is_rental_client = fields.Boolean(string='Is Rental Client')
    rental_client_since = fields.Date(string='Client Since')
    rental_notes = fields.Text(string='Rental Notes')
