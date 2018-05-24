# -*- coding: utf-8 -*-
# Copyright 2015-2018 Quartile Limted
# Copyright 2017 eHanse
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Product List Price Update List View',
    'version': '8.0.1.5.',
    'author': 'Quartile Limited, eHanse',
    'website': 'https://www.quartile.co',
    'category': 'Product',
    'depends': [
        "sale",
        "stock",
        "product_offer",
    ],
    'description': """
* Adds a menu item 'Product List Price' to facilitate list price update
    """,
    'data': [
        'views/product_product_views.xml',
    ],
    'installable': True,
}
