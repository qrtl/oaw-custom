# -*- coding: utf-8 -*-
# Copyright 2015-2017 Rooms For (Hong Kong) Limted T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Product List Price Update List View',
    'version': '8.0.1.3.0',
    'author': 'Rooms For (Hong Kong) Ltd T/A OSCG',
    'website': 'https://www.odoo-asia.com',
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
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
