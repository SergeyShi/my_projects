{
    'name': 'IT Outsource',
    'summary': 'Server Rental Management',
    'description': 'Module for managing server rentals and it services',
    'website': 'https://github.com/SergeyShi/odoo-modules/',
    'author': 'Serhii Shi',
    'category': 'Services',
    'license': 'LGPL-3',
    'version': '17.0.1.0.0',

    'depends': [
        'base',
        'account',
        'mail'
    ],
    'data': [
        'security/ir_module_category.xml',
        'security/security_groups.xml',
        'security/ir.model.access.csv',

        'data/email_template.xml',
        'data/server_rental_invoice_sequence.xml',
        'data/ir_sequence_data.xml',

        'views/it_outsource_menu_views.xml',
        'views/it_outsource_rental_product_views.xml',
        'views/it_outsource_contract_views.xml',
        'views/it_outsource_invoice_views.xml',
        'views/it_outsource_payment_views.xml',
        'views/it_outsource_res_partner_views.xml',
        'views/it_outsource_service_act_views.xml',

        'wizard/invoice_wizard_views.xml',

        'report/invoice_report.xml',
        'report/invoice_report_template.xml',
        'report/service_report.xml',

        'data/demo_data.xml',
    ],
    'demo': ['data/demo_data.xml'],
    'installable': True,
    'auto_install': False,
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/image(1).png',
    ],
}

