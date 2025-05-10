from odoo import models, fields, api


class RentalProduct(models.Model):
    _name = 'it.outsource.product'
    _description = 'Server or Service'

    name = fields.Char(string='Name')
    type = fields.Selection([
        ('server', 'Server'),
        ('service', 'Service')
    ], string='Type', required=True)

    price = fields.Monetary(
        string='Price',
        required=True,
        currency_field='currency_id'
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id.id
    )

    #    Технічні характеристики для серверів
    cpu_count = fields.Integer(string='CPU Count')
    ram_gb = fields.Float(string='RAM (GB)')
    disk_space_gb = fields.Float(string='Disk Space (GB)')

    def action_generate_name(self):
        self.ensure_one()
        if self.type == 'server':
            self.name = f"Сервер {self.cpu_count} CPU, {self.ram_gb} ГБ RAM"
        else:
            self.name = f"Послуга {self.price} {self.currency_id.symbol or ''}"

        self.env['ir.ui.view'].invalidate_model(['name'])
        return {
            'type': 'ir.actions.client',
            'tag': 'reload_context',
            # 'params': {
            #     'message': 'Назву згенеровано!',
            #     'type': 'success',
            #     'sticky': False,
            # }
        }
