# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Correct List Price Update Currency',
    'version': '8.0.1.0.0',
    'author': 'Quartile Limited',
    'website': 'https://www.quartile.co',
    'category': 'Product',
    'depends': [
        "sale",
        "stock",
        "product_offer",
    ],
    'description': """
* Adds a menu item 'Correct List Price Update Currency' to facilitate list 
price (currency) update
    """,
    'data': [
        'views/product_template_views.xml',
    ],
    'installable': True,
}
