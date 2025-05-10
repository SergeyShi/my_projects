from odoo import models, fields, api
from datetime import date, timedelta


class InvoiceWizard(models.TransientModel):
    _name = 'it.outsource.invoice.wizard'
    _description = 'Invoice Generation Wizard'

    date = fields.Date(string='Invoice Date', default=fields.Date.today)
    include_active = fields.Boolean(string='Include Active Contracts', default=True)
    include_expiring = fields.Boolean(string='Include Expiring Contracts')
    days_to_expire = fields.Integer(
        string='Days to Expire',
        default=30,
        help="Include contracts expiring in this many days",
        required=True
    )

    @api.constrains('days_to_expire')
    def _check_days_to_expire(self):
        for record in self:
            if record.days_to_expire < 1:
                raise models.ValidationError("Days to expire must be at least 1")

    def action_generate_invoices(self):
        self.ensure_one()
        Contract = self.env['it.outsource.contract']

        # Base domain for active contracts
        domain = [('state', '=', 'active')]

        # Build conditions based on wizard selections
        conditions = []
        if self.include_active:
            conditions.append([])  # All active contracts

        if self.include_expiring:
            expiration_date = date.today() + timedelta(days=self.days_to_expire)
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
                    'quantity': 1,  # Можна змінити на потрібну кількість
                    'price_unit': product.price,  # Беремо ціну з продукту
                    'description': product.name,  # Опис з продукту
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
