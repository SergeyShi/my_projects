from odoo import models, fields, api

class Contract(models.Model):
    _name = 'it.outsource.contract'
    _description = 'Services/Rental Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Name',
        compute='_compute_name',
        store=True,
        readonly=False,
        required=False)

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Client',
        required=True,
        tracking=True)

    number = fields.Char(string='Contract Number',
                         required=True,
                         default='New',
                         tracking=True)

    start_date = fields.Date(string='Start Date',
                             default=fields.Date.today,
                             tracking=True)
    end_date = fields.Date(string='End Date')

    product_ids = fields.Many2many(
        comodel_name='it.outsource.product',
        string='Services')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    notes = fields.Text(string='Notes')
    monthly_total = fields.Float(
        string='Monthly Total')

    invoice_ids = fields.One2many(
        comodel_name='it.outsource.invoice',
        inverse_name='contract_id',
        string='Invoices')

    service_report_ids = fields.One2many(
        'it.outsource.service.act',
        'contract_id',
        string='Service Reports'
    )

    @api.depends('number', 'partner_id.name')
    def _compute_name(self):
        for record in self:
            number_part = record.number or ''
            client_part = record.partner_id.name or ''
            record.name = f"{number_part} / {client_part}"

    def action_activate(self):
        self.write({'state': 'active'})

    def action_expire(self):
        self.write({'state': 'expired'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})
