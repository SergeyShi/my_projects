from datetime import date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class InvoiceWizard(models.TransientModel):
    """Wizard for creating invoices from contracts.
    This wizard allows users to create invoices for active contracts.
    It provides functionality to select contracts and generate invoices
    with the appropriate lines based on the contract products.
    """
    _name = 'it.outsource.invoice.wizard'
    _description = 'Invoice Generation Wizard'

    date = fields.Date(
        string='Invoice Date',
        required=True,
        default=fields.Date.context_today,
        help='Date of the invoice'
    )
    include_active = fields.Boolean(
        string='Include Active Contracts',
        default=True)
    include_expiring = fields.Boolean(string='Include Expiring Contracts')
    days_to_expire = fields.Integer(
        string='Days to Expire',
        default=30,
        help="Include contracts expiring in this many days",
        required=True
    )

    @api.constrains('days_to_expire')
    def _check_days_to_expire(self):
        """Validate the days to expire.
        This method ensures that the days to expire is at least 1.
        Raises:
            ValidationError: If the days to expire is less than 1
        """
        for record in self:
            if record.days_to_expire < 1:
                raise ValidationError(_("Days to expire must be at least 1"))

    @api.constrains('due_date')
    def _check_due_date(self):
        """Validate the due date.
        This method ensures that the due date is not before the invoice date.
        Raises:
            ValidationError: If the due date is before the invoice date
        """
        for wizard in self:
            if wizard.due_date < wizard.date:
                raise ValidationError(_('Due date cannot be before invoice date.'))

    def action_generate_invoices(self):
        """Generate invoices for selected contracts.
        This method generates invoices for each selected contract, including
        invoice lines for each product in the contract.
        Returns:
            dict: Action to view the created invoices
        """
        self.ensure_one()
        Contract = self.env['it.outsource.contract']

        # Base domain for active contracts
        domain = [('state', '=', 'active')]

        # Build conditions based on wizard selections
        conditions = []
        if self.include_active:
            conditions.append([])  # All active contracts

        if self.include_expiring:
            expiration_date = (date.today() +
                               timedelta(days=self.days_to_expire))
            conditions.append([('end_date', '<=', expiration_date)])

        # Combine conditions with OR if both are selected
        if len(conditions) > 1:
            domain = ['|'] + conditions[0] + conditions[1]
        elif conditions:
            domain += conditions[0]
        else:
            return {'type': 'ir.actions.act_window_close'}

        # Find matching contracts
        contracts = Contract.search(domain)

        # Batch create invoices with lines
        invoices = self.env['it.outsource.invoice']
        for contract in contracts:
            # Prepare invoice values
            invoice_vals = {
                'contract_id': contract.id,
                'date': self.date,
                'line_ids': []
            }

            # Add products/services from contract to invoice lines
            for product in contract.product_ids:
                line_vals = {
                    'product_type': product.type,
                    'product_id': product.id,
                    'quantity': 1,
                    'price_unit': product.price,
                    'description': product.name,
                }
                invoice_vals['line_ids'].append((0, 0, line_vals))

            # Create invoice
            invoice = self.env['it.outsource.invoice'].create(invoice_vals)
            invoices += invoice

        # Return action to view created invoices
        return {
            'name': 'Generated Invoices',
            'type': 'ir.actions.act_window',
            'res_model': 'it.outsource.invoice',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', invoices.ids)],
            'context': {'create': False},
        }
