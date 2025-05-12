from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Invoice(models.Model):
    """Invoice model for IT outsourcing.
    This class represents an invoice document that records services or products
    provided to clients. It includes information about the client, contract,
    invoice date, due date, items invoiced, and payment status.
    """
    _name = 'it.outsource.invoice'
    _description = 'Rental Invoice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(
        string='Invoice Number',
        required=True,
        index=True,
        copy=False,
        default='New',
        help='Unique identifier for the invoice'
    )
    contract_id = fields.Many2one(
        comodel_name='it.outsource.contract',
        string='Contract',
        required=True,
        ondelete='restrict',
        help='The contract under which services were provided'
    )

    date = fields.Date(
        string='Invoice Date',
        default=fields.Date.context_today,
        required=True,
        tracking=True,
        help='Date when the invoice was created'
    )
    due_date = fields.Date(
        compute='_compute_due_date',
        store=True,
        readonly=False,
        help='Date when the invoice payment is due'
    )
    amount = fields.Monetary(
        compute='_compute_amount',
        store=True,
        currency_field='currency_id',
        help='Total amount for all items'
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='Status',
        default='draft',
        tracking=True,
        group_expand='_expand_states',
        help='Current state of the invoice'
    )
    payment_ids = fields.One2many(
        comodel_name='it.outsource.payment',
        inverse_name='invoice_id',
        string='Payments',
        copy=False,
        help='List of payments associated with the invoice'
    )
    paid_amount = fields.Monetary(
        compute='_compute_paid_amount',
        currency_field='currency_id',
        help='Total amount that has been paid'
    )
    residual = fields.Monetary(
        string='Balance Due',
        compute='_compute_residual',
        currency_field='currency_id',
        help='Remaining amount to be paid'
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id
    )
    line_ids = fields.One2many(
        comodel_name='it.outsource.invoice.line',
        inverse_name='invoice_id',
        string='Invoice Lines',
        copy=True,
        help='List of items being invoiced'
    )

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.depends('line_ids.amount')
    def _compute_amount(self):
        """Compute the total amount for the invoice.
        This method calculates the total amount by summing up the amounts
        of all invoice lines.
        """
        for invoice in self:
            invoice.amount = sum(invoice.line_ids.mapped('amount'))

    @api.depends('date')
    def _compute_due_date(self):
        """Compute the due date for the invoice.
        This method calculates the due date by adding 30 days to the invoice date.
        """
        for invoice in self:
            if invoice.date:
                invoice.due_date = invoice.date + timedelta(days=30)

    @api.depends('payment_ids.amount')
    def _compute_paid_amount(self):
        """Compute the total paid amount.
        This method calculates the total amount that has been paid by summing
        up all confirmed payments.
        """
        for invoice in self:
            invoice.paid_amount = sum(invoice.payment_ids.mapped('amount'))
            # if invoice.paid_amount >= invoice.amount:
            #     invoice.state = 'paid'

    @api.depends('amount', 'paid_amount')
    def _compute_residual(self):
        """Compute the residual amount.
        This method calculates the remaining amount to be paid by subtracting
        the paid amount from the total amount.
        """
        for invoice in self:
            invoice.residual = invoice.amount - invoice.paid_amount

    @api.model
    def create(self, vals):
        """Create a new invoice with a sequence number.
        This method overrides the create method to automatically generate
        sequence numbers for new invoices.
        Args:
            vals (dict): Dictionary containing values for the new record
        Returns:
            record: Newly created invoice
        """
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'it.outsource.invoice') or 'New'
        return super().create(vals)

    def _get_report_base_filename(self):
        """
        Returns the base filename for the doctor's report.
        """
        return f'Invoice_{self.name}_{self.date}'

    def action_send(self):
        """Send the invoice.
        This method changes the state of the invoice to 'sent'.
        It also validates that the invoice has at least one line.
        Raises:
            ValidationError: If the invoice has no lines
        """
        self.ensure_one()

        template = self.env.ref(
            'your_module_name.email_template_rental_invoice',
            raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)

        self.write({'state': 'sent'})
        return True

    def action_paid(self):
        """Mark the invoice as paid.
        This method marks the invoice as paid if the residual amount is 0 or less.
        Returns:
            bool: True if the invoice was marked as paid, False otherwise
        """
        self.ensure_one()
        if self.residual <= 0:
            self.write({'state': 'paid'})
        return True

    def action_cancel(self):
        """Cancel the invoice.
        This method changes the state of the invoice to 'cancelled'.
        It requires a cancellation reason to be provided.
        Raises:
            ValidationError: If no cancellation reason is provided
        """
        self.ensure_one()
        self.write({'state': 'cancelled'})
        return True

    def action_draft(self):
        """Mark the invoice as draft.
        This method changes the state of the invoice to 'draft'.
        Returns:
            bool: True if the invoice was marked as draft, False otherwise
        """
        self.ensure_one()
        self.write({'state': 'draft'})
        return True

    @api.constrains('due_date')
    def _check_due_date(self):
        """Validate the due date.
        This method ensures that the due date is not before the invoice date.
        Raises:
            ValidationError: If the due date is before the invoice date
        """
        for invoice in self:
            if invoice.due_date < invoice.date:
                raise ValidationError(_('Due date cannot be before invoice date.'))

    @api.constrains('line_ids')
    def _check_lines(self):
        """Validate invoice lines.
        This method ensures that the invoice has at least one line.
        Raises:
            ValidationError: If the invoice has no lines
        """
        for invoice in self:
            if not invoice.line_ids:
                raise ValidationError(_('Invoice must have at least one line.'))
