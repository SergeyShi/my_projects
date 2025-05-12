from odoo import models, fields, api


class ServiceAct(models.Model):
    """Service Act model for IT outsourcing.
    This class represents a service act document that records services provided
    to clients. It includes information about the client, contract, services
    provided, and their costs.
    """

    _name = 'it.outsource.service.act'
    _description = 'Service Act'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Number',
        required=True,
        copy=False,
        readonly=True,
        default='New',
        help='Unique identifier for the service act'
    )

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id
    )

    contract_id = fields.Many2one(
        comodel_name='it.outsource.contract',
        string='Contract',
        required=True,
        tracking=True,
        help='The contract under which services were provided'
    )

    date = fields.Date(
        required=True,
        default=fields.Date.context_today,
        tracking=True,
        help='Date when services were provided'
    )

    # state = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('validated', 'Validated'),
    #     ('canceled', 'Canceled')
    # ], string='Status', default='draft', tracking=True,
    #    help='Current state of the service act')

    line_ids = fields.One2many(
        comodel_name='it.outsource.service.act.line',
        inverse_name='service_act_id',
        string='Service Lines',
        help='List of services provided'
    )

    amount_total = fields.Float(
        string='Total Amount',
        compute='_compute_amount_total',
        store=True,
        help='Total amount for all services'
    )

    description = fields.Text(
        help='Additional information about the services provided'
    )

    # cancel_reason = fields.Text(
    #     string='Cancellation Reason',
    #     help='Reason for canceling the service act'
    # )

    @api.depends('line_ids.subtotal')
    def _compute_amount_total(self):
        """Compute the total amount for the service act.
        This method calculates the total amount by summing up the subtotals
        of all service lines.
        """
        for act in self:
            act.amount_total = sum(act.line_ids.mapped('subtotal'))

    @api.model_create_multi
    def create(self, vals_list):
        """Create new service acts with sequence numbers.
        This method overrides the create method to automatically generate
        sequence numbers for new service acts.
        Args:
            vals_list (list): List of dictionaries containing values for new records
        Returns:
            recordset: Newly created service acts
        """
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('it.outsource.service.act') or 'New'
        return super().create(vals_list)

    # def action_validate(self):
    #     """Validate the service act.
    #
    #     This method changes the state of the service act to 'validated'.
    #     It also validates that the service act has at least one line.
    #
    #     Raises:
    #         ValidationError: If the service act has no lines
    #     """
    #     for act in self:
    #         if not act.line_ids:
    #             raise ValidationError('Cannot validate service act without lines.')
    #         act.state = 'validated'

    # def action_cancel(self):
    #     """Cancel the service act.
    #
    #     This method changes the state of the service act to 'canceled'.
    #     It requires a cancellation reason to be provided.
    #
    #     Raises:
    #         ValidationError: If no cancellation reason is provided
    #     """
    #     for act in self:
    #         if not act.cancel_reason:
    #             raise ValidationError('Please provide a reason for cancellation.')
    #         act.state = 'canceled'

    def print_report(self):
        return self.env.ref(
            'it_outsource.action_report_service_report').report_action(self)

    def _get_report_base_filename(self):
        """
        Returns the base filename for the doctor's report.
        """
        return f'Invoice_{self.name}_{self.date}'
