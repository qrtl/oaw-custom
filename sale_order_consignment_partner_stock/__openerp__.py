# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale Order Consignmnet Partner Stock',
    'summary': '',
    'version': '8.0.1.0.0',
    'category': 'Sales',
    'author': 'Quartile Limited',
    'website': 'https://www.quartile.co',
    'description': """
    """,
    "license": "AGPL-3",
    'depends': [
        'sale_line_quant',
        'supplier_stock',
        'view_adjustments',
    ],
    'data': [
        'views/supplier_stock_views.xml',
    ],
    'application': False,
}
