# -*- coding: utf-8 -*-
# Copyright 2016-2018 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Purchase View Adjust',
    'summary': "",
    'version': "8.0.2.0.0",
    'category': 'Purchases',
    'website': 'https://www.quartile.co',
    'author': 'Quartile Limited',
    'license': "AGPL-3",
    'description': """
* Adjust purchase related views.
    """,
    'application': False,
    'installable': True,
    'depends': [
        "purchase",
        "web_tree_image",
        "sale_line_quant_extended",
    ],
    'data': [
        'data/ir_actions.xml',
        'views/purchase_order_line_views.xml',
        'views/purchase_order_views.xml',
    ],
}
