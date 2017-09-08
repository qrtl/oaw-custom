# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Profit and Loss Report',
    'version': '8.0.2.0.0',
    'author': 'Quartile Limited',
    'website': 'https://www.odoo-asia.com',
    'category': 'Report',
    'depends': [
        'sale_line_quant_extended',
        'product_offer',
    ],
    'description': """
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/profit_loss_report_views.xml',
        'wizards/profit_loss_report_wizard_views.xml',
    ],
    'installable': True,
}
