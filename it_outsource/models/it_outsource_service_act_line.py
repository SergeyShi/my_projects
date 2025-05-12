from odoo import models, fields, api


class ServiceActLine(models.Model):
    """Service Act Line model for IT outsourcing.
    This class represents a line item in a service act. Each line contains
    information about a specific service or product provided, including
    quantity, price, and total amount.
    """
    _name = 'it.outsource.service.act.line'
    _description = 'Service Act Line'

    service_act_id = fields.Many2one(
        comodel_name='it.outsource.service.act',
        string='Service Act',
        required=True,
        ondelete='cascade',
        help='The service act this line belongs to'
    )

    product_id = fields.Many2one(
        comodel_name='it.outsource.product',
        string='Product',
        required=True,
        help='The product or service provided'
    )

    quantity = fields.Float(
        required=True,
        default=1.0,
        help='Quantity of the product or service'
    )

    price = fields.Float(
        required=True,
        help='Unit price of the product or service'
    )

    unit = fields.Char(default='hour')

    subtotal = fields.Float(
        compute='_compute_subtotal',
        store=True,
        help='Total amount for this line (quantity * price)'
    )

    @api.depends('quantity', 'price')
    def _compute_subtotal(self):
        """Compute the subtotal for each line.
        This method calculates the total amount for each line by multiplying
        the quantity by the unit price.
        """
        for line in self:
            line.subtotal = line.quantity * line.price
