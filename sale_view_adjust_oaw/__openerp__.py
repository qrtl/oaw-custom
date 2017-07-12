# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sales View Adjust OAW',
    'summary': '',
    'version': '8.0.1.0.1',
    'category': 'Sales',
    'author': 'Quartile Limited',
    'website': 'https://www.odoo-asia.com',
    'description': """
    """,
    "license": "AGPL-3",
    'application': False,
    'installable': True,
    'auto_install': False,
    'images' : [],
    'depends': [
        'sale',
        'web_tree_image',
    ],
    'data': [
        'views/sale_order_views.xml',
    ],
}
