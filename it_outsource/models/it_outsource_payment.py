from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Payment(models.Model):
    """Payment model for IT outsourcing.
    This class represents a payment made by a client for services or products.
    It tracks payment details including amount, method, date, and status.
    """
    _name = 'it.outsource.payment'
    _description = 'Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Number',
        required=True,
        copy=False,
        readonly=True,
        default='New',
        help='Unique identifier for the payment'
    )

    invoice_id = fields.Many2one(
        comodel_name='it.outsource.invoice',
        string='Invoice',
        required=True,
        tracking=True,
        help='The invoice this payment is for'
    )

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Client',
        related='invoice_id.contract_id.partner_id',
        store=True,
        help='The client who made the payment'
    )

    amount = fields.Float(
        required=True,
        tracking=True,
        help='Payment amount'
    )

    payment_method = fields.Selection([
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('card', 'Card')
    ],
        required=True,
        tracking=True,
        help='Method used for payment')

    date = fields.Date(
        string='Payment Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
        help='Date when payment was made'
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled')
    ], string='Status',
        default='draft',
        tracking=True,
        help='Current state of the payment')

    notes = fields.Text(
        help='Additional information about the payment'
    )

    cancel_reason = fields.Text(
        string='Cancellation Reason',
        help='Reason for canceling the payment'
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Create new payments with sequence numbers.
        This method overrides the create method to automatically generate
        sequence numbers for new payments.
        Args:
            vals_list (list): List of dictionaries containing values for new records
        Returns:
            recordset: Newly created payments
        """
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('it_outsource.payment') or 'New'
        return super().create(vals_list)

    def action_confirm(self):
        """Confirm the payment.
        Validates payment amount and updates invoice status if fully paid.
        """
        for payment in self:
            if payment.amount > payment.invoice_id.residual:
                raise ValidationError(_('Payment amount cannot exceed invoice amount.'))

            payment.state = 'confirmed'

            # recompute via stored field triggers
            payment.invoice_id._compute_paid_amount()
            payment.invoice_id._compute_residual()

            # refresh to ensure residual is up to date
            payment.invoice_id.flush(['paid_amount', 'residual'])

            if payment.invoice_id.residual <= 0:
                payment.invoice_id.write({'state': 'paid'})

        # if single record: return form view for invoice
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'it.outsource.invoice',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
            'target': 'current',
        }

    def action_cancel(self):
        """Cancel the payment.
        This method changes the state of the payment to 'canceled'.
        It requires a cancellation reason to be provided.
        Raises:
            ValidationError: If no cancellation reason is provided
        """
        for payment in self:
            if not payment.cancel_reason:
                raise ValidationError(_('Please provide a reason for cancellation.'))
            payment.state = 'canceled'

    @api.constrains('amount')
    def _check_amount(self):
        """Validate the payment amount.
        This method ensures that the payment amount is positive.
        Raises:
            ValidationError: If the amount is negative or zero
        """
        for payment in self:
            if payment.amount <= 0:
                raise ValidationError(_('Payment amount must be positive.'))

    @api.constrains('date')
    def _check_date(self):
        """Validate the payment date.
        This method ensures that the payment date is not in the future.
        Raises:
            ValidationError: If the date is in the future
        """
        for payment in self:
            if payment.date > fields.Date.context_today(self):
                raise ValidationError(_('Payment date cannot be in the future.'))

    @api.onchange('invoice_id')
    def _onchange_invoice_id(self):
        if self.invoice_id and not self.amount:
            self.amount = self.invoice_id.residual
