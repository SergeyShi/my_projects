from odoo import models, fields, api


class InvoiceLine(models.Model):
    """Invoice Line model for IT outsourcing.
    This class represents a line item in an invoice. Each line contains
    information about a specific product or service being invoiced, including
    quantity, price, and total amount.
    """
    _name = 'it.outsource.invoice.line'
    _description = 'Invoice Line'

    invoice_id = fields.Many2one(
        comodel_name='it.outsource.invoice',
        string='Invoice',
        required=True,
        ondelete='cascade')

    product_type = fields.Selection([
        ('server', 'Server'),
        ('service', 'Service')
    ], string='Type', required=True)

    product_id = fields.Many2one(
        comodel_name='it.outsource.product',
        string='Product',
        domain="[('product_type', '=', product_type)]"
    )

    description = fields.Char()
    quantity = fields.Float(default=1.0)
    price_unit = fields.Float(string='Unit Price')
    amount = fields.Float(
        compute='_compute_amount',
        store=True)

    @api.onchange('product_type')
    def _onchange_product_type(self):
        self.product_id = False
        self.price_unit = 0.0
        self.amount = 0.0

    @api.onchange('product_id')
    def _onchange_product(self):
        if self.product_id:
            self.description = self.product_id.name
            self.price_unit = self.product_id.price
            self._compute_amount()

    @api.depends('quantity', 'price_unit')
    def _compute_amount(self):
        for line in self:
            line.amount = line.quantity * line.price_unit

    @api.onchange('quantity', 'price_unit')
    def _onchange_quantity_or_price(self):
        self._compute_amount()
