from odoo import models, fields, api


class ServiceReport(models.Model):
    _name = 'it.outsource.service.act'
    _description = 'Work Completion Certificate'

    name = fields.Char(
        string='Report Name',
        required=True, default='New'
    )

    contract_id = fields.Many2one(
        comodel_name='it.outsource.contract',
        string='Contract', required=True
    )

    report_date = fields.Date(
        string='Report Date',
        default=fields.Date.context_today, required=True
    )

    description = fields.Text(
        string='Description of Services'
    )

    amount = fields.Monetary(
        string='Total Amount', currency_field='currency_id'
    )

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency', required=True,
        default=lambda self: self.env.company.currency_id
    )

    def print_report(self):
        return self.env.ref('it.outsource.action_report_service_report').report_action(self)

    def _get_report_base_filename(self):
        """
        Returns the base filename for the doctor's report.
        """
        return f'Invoice_{self.name}_{self.date}'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('it.outsource.service.act') or 'New'
        return super().create(vals)
