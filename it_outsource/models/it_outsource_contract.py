from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Contract(models.Model):
    """Contract model for IT outsourcing.
    This class represents a contract between a client and the IT outsourcing
    company. It includes information about the client, services provided,
    contract period, and status.
    """

    _name = 'it.outsource.contract'
    _description = 'Services/Rental Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        compute='_compute_name',
        store=True,
        required=False,
        string='Number',
        copy=False,
        readonly=True,
        default='New',
        help='Unique identifier for the contract'
    )

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Client',
        required=True,
        tracking=True,
        help='The client who signed the contract'
    )

    number = fields.Char(
        string='Contract Number',
        required=True,
        default='New',
        tracking=True)

    start_date = fields.Date(
        default=fields.Date.today,
        tracking=True,
        help='Date when the contract starts'
    )

    end_date = fields.Date(
        required=True,
        tracking=True,
        help='Date when the contract ends'
    )

    product_ids = fields.Many2many(
        comodel_name='it.outsource.product',
        string='Services',
        required=True,
        help='Products and services included in the contract'
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True, help='Current state of the contract')

    notes = fields.Text(
        help='Additional information about the contract'
    )

    monthly_total = fields.Float(
        store=True,
        help='Total monthly cost of all products'
    )

    cancel_reason = fields.Text(
        string='Cancellation Reason',
        help='Reason for canceling the contract'
    )

    invoice_ids = fields.One2many(
        comodel_name='it.outsource.invoice',
        inverse_name='contract_id',
        string='Invoices'
    )

    service_report_ids = fields.One2many(
        comodel_name='it.outsource.service.act',
        inverse_name='contract_id',
        string='Service Reports'
    )

    @api.depends('number', 'partner_id.name')
    def _compute_name(self):
        for record in self:
            number_part = record.number or ''
            client_part = record.partner_id.name or ''
            record.name = f"{number_part} / {client_part}"

    @api.model_create_multi
    def create(self, vals_list):
        """Create new contracts with sequence numbers.
        This method overrides the create method to automatically generate
        sequence numbers for new contracts.
        Args:
            vals_list (list): List of dictionaries containing values for new records
        Returns:
            recordset: Newly created contracts
        """
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('it_outsource.contract') or 'New'
        return super().create(vals_list)

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_activate(self):
        """Confirm the contract.
        This method changes the state of the contract to 'active'.
        It also validates that the contract has at least one product.
        Raises:
            ValidationError: If the contract has no products
        """
        for contract in self:
            if not contract.product_ids:
                raise ValidationError(_('Contract must have at least one product.'))
            contract.state = 'active'

    def action_expire(self):
        self.write({'state': 'expired'})

    def action_cancel(self):
        """Cancel the contract.
        This method changes the state of the contract to 'cancelled'.
        It requires a cancellation reason to be provided.
        Raises:
            ValidationError: If no cancellation reason is provided
        """
        for contract in self:
            if not contract.cancel_reason:
                raise ValidationError(_('Please provide a reason for cancellation.'))
            contract.state = 'cancelled'

    @api.constrains('end_date')
    def _check_end_date(self):
        """Validate the end date.
        This method ensures that the end date is not before the start date.
        Raises:
            ValidationError: If the end date is before the start date
        """
        for contract in self:
            if contract.end_date < contract.start_date:
                raise ValidationError(_('End date cannot be before start date.'))

    @api.constrains('start_date')
    def _check_start_date(self):
        """Validate the start date.
        This method ensures that the start date is not in the past.
        Raises:
            ValidationError: If the start date is in the past
        """
        for contract in self:
            if contract.start_date < fields.Date.context_today(self):
                raise ValidationError(_('Start date cannot be in the past.'))

    @api.constrains('product_ids')
    def _check_products(self):
        """Validate contract products.
        This method ensures that the contract has at least one product.
        Raises:
            ValidationError: If the contract has no products
        """
        for contract in self:
            if not contract.product_ids:
                raise ValidationError(_('Contract must have at least one product.'))
