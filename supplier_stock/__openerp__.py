# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limted
# Copyright 2017 eHanse
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Supplier Stock',
    'category': 'Stock',
    'version': '8.0.1.2.2',
    'author': 'Quartile Limited T/A OSCG',
    'website': 'https://www.odoo-asia.com',
    'depends': [
        'purchase',
    ],
    'summary':"""""",
    'description': """
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/supplier_location_views.xml',
        'views/supplier_stock_views.xml',
    ],
    'installable': True,
}
