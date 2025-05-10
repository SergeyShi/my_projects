from odoo import models, fields, api


class InvoiceLine(models.Model):
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
        domain="[('type', '=', product_type)]"
    )

    description = fields.Char(string='Description')
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Unit Price')
    amount = fields.Float(
        string='Amount',
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
