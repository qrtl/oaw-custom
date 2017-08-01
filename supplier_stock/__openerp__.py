# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limted
# Copyright 2017 eHanse
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Supplier Stock',
    'category': 'Stock',
    'version': '8.0.1.2.3',
    'author': 'Quartile Limited',
    'website': 'https://www.odoo-asia.com',
    'depends': [
        'purchase',
    ],
    'summary':"""""",
    'description': """
    """,
    'data': [
        'data/supplier_stock_data.xml',
        'security/ir.model.access.csv',
        'views/supplier_location_views.xml',
        'views/supplier_stock_views.xml',
        'wizards/supplier_stock_revaluation_wizard_view.xml',
    ],
    'installable': True,
}
