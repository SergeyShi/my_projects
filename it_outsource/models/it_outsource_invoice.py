from odoo import models, fields, api
from datetime import timedelta

class Invoice(models.Model):
    _name = 'it.outsource.invoice'
    _description = 'Rental Invoice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(
        string='Invoice Number',
        required=True,
        index=True,
        copy=False,
        default='New'
    )
    contract_id = fields.Many2one(
        'it.outsource.contract',
        string='Contract',
        required=True,
        ondelete='restrict'  # Забороняє видалення контракту з пов'язаними інвойсами
    )


    date = fields.Date(
        string='Invoice Date',
        default=fields.Date.context_today,
        required=True
    )
    due_date = fields.Date(
        string='Due Date',
        compute='_compute_due_date',
        store=True,
        readonly=False  # Дозволяє ручне редагування
    )
    amount = fields.Monetary(
        string='Amount',
        compute='_compute_amount',
        store=True,
        currency_field='currency_id'
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='Status',
        default='draft',
        tracking=True,
        group_expand='_expand_states'
    )
    payment_ids = fields.One2many(
        'it.outsource.payment',
        'invoice_id',
        string='Payments',
        copy=False
    )
    paid_amount = fields.Monetary(
        string='Paid Amount',
        compute='_compute_paid_amount',
        currency_field='currency_id'
    )
    residual = fields.Monetary(
        string='Balance Due',
        compute='_compute_residual',
        currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id
    )
    line_ids = fields.One2many(
        'it.outsource.invoice.line',
        'invoice_id',
        string='Invoice Lines',
        copy=True
    )

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.depends('line_ids.amount')
    def _compute_amount(self):

        for invoice in self:
            invoice.amount = sum(invoice.line_ids.mapped('amount'))

    @api.depends('date')
    def _compute_due_date(self):

        for invoice in self:
            if invoice.date:
                invoice.due_date = invoice.date + timedelta(days=30)

    @api.depends('payment_ids.amount')
    def _compute_paid_amount(self):

        for invoice in self:
            invoice.paid_amount = sum(invoice.payment_ids.mapped('amount'))

    @api.depends('amount', 'paid_amount')
    def _compute_residual(self):

        for invoice in self:
            invoice.residual = invoice.amount - invoice.paid_amount

    @api.model
    def create(self, vals):

        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('it.outsource.invoice') or 'New'
        return super().create(vals)

    def _get_report_base_filename(self):
        """
        Returns the base filename for the doctor's report.
        """
        return f'Invoice_{self.name}_{self.date}'

    def action_send(self):
        self.ensure_one()

        template = self.env.ref('your_module_name.email_template_rental_invoice', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)

        self.write({'state': 'sent'})
        return True

    def action_paid(self):

        self.ensure_one()
        if self.residual <= 0:
            self.write({'state': 'paid'})
        return True

    def action_cancel(self):

        self.ensure_one()
        self.write({'state': 'cancelled'})
        return True

    def action_draft(self):

        self.ensure_one()
        self.write({'state': 'draft'})
        return True
