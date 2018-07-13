# -*- coding: utf-8 -*-
# Copyright 2017-2018 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sales View Adjust OAW',
    'summary': '',
    'version': '8.0.1.1.0',
    'category': 'Sales',
    'author': 'Quartile Limited',
    'website': 'https://www.quartile.co',
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
        'sale_line_quant',
        'sale_margin'
    ],
    'data': [
        'data/ir_actions.xml',
        'views/sale_order_views.xml',
    ],
}
