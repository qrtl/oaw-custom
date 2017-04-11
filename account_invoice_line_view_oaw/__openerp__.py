# -*- coding: utf-8 -*-
# Copyright 2015-2017 Rooms For (Hong Kong) Limted T/A OSCG
# Copyright 2017 eHanse
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Invoice Line View OAW',
    'version': '8.0.1.0.0',
    'category': 'Account',
    'summary': 'Adds Invoice Line menu item',
    'description': """
Main Features
==================================================
* Add menu item Invoice Lines
* Captures exchange rates as of the invoice dates and shows the base currency\
 amounts in the output. 

    """,
    'author': 'Rooms For (Hong Kong) Limited T/A OSCG',
    'website': 'http://odoo-asia.com',
    "license": "AGPL-3",
    'images' : [],
    'depends': [
        'account',
        'sale',
        'purchase',
        'sale_line_quant'
    ],
    'data': [
         'views/account_invoice_line_views.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
