from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'


    rental_contract_ids = fields.One2many('it.outsource.contract', 'partner_id', string='Rental Contracts')

    is_rental_client = fields.Boolean(string='Is Rental Client')
    rental_client_since = fields.Date(string='Client Since')
    rental_notes = fields.Text(string='Rental Notes')
