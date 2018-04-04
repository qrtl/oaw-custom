# -*- coding: utf-8 -*-
# Copyright 2017-2018 Quartile Limited
# Copyright 2017 eHanse
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Supplier Stock',
    'category': 'Stock',
    'version': '8.0.1.3.0',
    'author': 'Quartile Limited',
    'website': 'https://www.quartile.co',
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
