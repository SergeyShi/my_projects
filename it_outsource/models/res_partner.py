from odoo import models, fields, api


class ResPartner(models.Model):
    """Partner model extension for IT outsourcing functionality.
    This class extends the base partner model to add IT outsourcing specific fields
    and functionality. It adds fields for tracking contract-related information
    and provides methods for managing contract relationships.
    """

    _inherit = 'res.partner'

    rental_contract_ids = fields.One2many(
        comodel_name='it.outsource.contract',
        inverse_name='partner_id',
        string='Rental Contracts')

    is_rental_client = fields.Boolean()
    rental_client_since = fields.Date()
    rental_notes = fields.Text()

    contract_ids = fields.One2many(
        comodel_name='it.outsource.contract',
        inverse_name='partner_id',
        string='Contracts',
        help='List of contracts associated with this partner'
    )

    contract_count = fields.Integer(
        compute='_compute_contract_count',
        help='Number of contracts associated with this partner'
    )

    @api.depends('contract_ids')
    def _compute_contract_count(self):
        """Compute the number of contracts for each partner.
        This method calculates the total number of contracts associated with
        each partner and stores it in the contract_count field.
        """
        for partner in self:
            partner.contract_count = len(partner.contract_ids)
