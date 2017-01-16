# -*- coding: utf-8 -*-
# Copyright 2015-2017 Rooms For (Hong Kong) Limted T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Product List Price Update List View',
    'version': '8.0.1.0.1',
    'author': 'Rooms For (Hong Kong) Ltd T/A OSCG',
    'website': 'http://www.openerp-asia.net',
    'category': 'Product',
    'depends': ["product", "sale", "stock"],
    'description': """
* Adds a menu item 'Product List Price' to facilitate list price update
    """,
    'data': [
        'product_view.xml',
    ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
