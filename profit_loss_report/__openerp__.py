# -*- coding: utf-8 -*-
# Copyright 2017-2018 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Profit and Loss Report',
    'version': '8.0.3.0.0',
    'author': 'Quartile Limited',
    'website': 'https://www.quartile.co',
    'category': 'Report',
    'depends': [
        'account_invoice_paid_date_currency',
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
