from odoo import models, fields, api

class Payment(models.Model):
    _name = 'it.outsource.payment'
    _description = 'Invoice Payment'

    name = fields.Char(string='Payment Reference', required=True, default='New')
    invoice_id = fields.Many2one('it.outsource.invoice', string='Invoice', required=True)
    date = fields.Date(string='Payment Date', default=fields.Date.today)
    amount = fields.Float(string='Amount', required=True)
    # partner_id = fields.Many2one('res.partner', string='Client', required=True)
    payment_method = fields.Selection([
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('card', 'Credit Card'),
        ('other', 'Other')
    ], string='Payment Method', default='bank')
    notes = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('it.outsource.payment') or 'New'
        return super().create(vals)

    @api.onchange('invoice_id')
    def _onchange_invoice_id(self):
        if self.invoice_id and not self.amount:
            self.amount = self.invoice_id.residual
