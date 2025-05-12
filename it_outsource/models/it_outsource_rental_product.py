from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class RentalProduct(models.Model):
    """Rental product model for IT outsourcing.
    This class represents a product that can be rented out to clients.
    It includes information about the product specifications, rental price,
    and availability status.
    """
    _name = 'it.outsource.product'
    _description = 'Rental and Services'

    name = fields.Char(
        required=True,
        help='Name of the rental product'
    )

    product_type = fields.Selection([
        ('server', 'Server'),
        ('service', 'Service')
    ], string='Type',
        required=True,
        help='Type of the product (server or service)')

    price = fields.Float(
        required=True,
        help='Monthly rental price'
    )

    cpu_count = fields.Integer(string='CPU Count')
    ram_gb = fields.Float(string='RAM (GB)')
    disk_space_gb = fields.Float(string='Disk Space (GB)')

    state = fields.Selection([
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('maintenance', 'Maintenance')
    ], string='Status',
        default='available',
        help='Current status of the product')

    contract_ids = fields.Many2many(
        comodel_name='it.outsource.contract',
        string='Contracts',
        help='Contracts where this product is used'
    )

    @api.constrains('price')
    def _check_price(self):
        """Validate the product price.
        This method ensures that the price is positive.
        Raises:
            ValidationError: If the price is negative or zero
        """
        for product in self:
            if product.price <= 0:
                raise ValidationError(_('Price must be positive.'))

    @api.onchange('cpu_count', 'ram_gb', 'product_type')
    def _onchange_generate_name(self):
        for record in self:
            if record.product_type == 'server':
                record.name = f"Server {record.cpu_count} CPU, {record.ram_gb} ГБ RAM"
            else:
                record.name = "Service"

    def action_rent(self):
        """Mark the product as rented.
        This method changes the state of the product to 'rented'.
        """
        self.write({'state': 'rented'})

    def action_return(self):
        """Mark the product as available.
        This method changes the state of the product to 'available'.
        """
        self.write({'state': 'available'})

    def action_maintenance(self):
        """Mark the product as under maintenance.
        This method changes the state of the product to 'maintenance'.
        """
        self.write({'state': 'maintenance'})
