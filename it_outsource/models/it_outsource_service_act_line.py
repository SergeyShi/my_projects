from odoo import models, fields, api

class ItOutsourceServiceActLine(models.Model):
    _name = 'it.outsource.service.act.line'
    _description = 'Service Act Line'

    act_id = fields.Many2one('it.outsource.service.act', string="Акт", required=True, ondelete='cascade')
    name = fields.Char(string="Опис послуги", required=True)
    quantity = fields.Float(string="Кількість", default=1.0)
    price_unit = fields.Float(string="Ціна за одиницю", required=True)
    subtotal = fields.Monetary(string="Сума", compute="_compute_subtotal", store=True)
    currency_id = fields.Many2one(related='act_id.currency_id', store=True, readonly=True)

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit