# -*- coding: utf-8 -*-
# Copyright 2017 Rooms For (Hong Kong) Limted T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Supplier Stock',
    'category': 'Stock',
    'version': '8.0.1.0.0',
    'author': 'Rooms For (Hong Kong) Limited T/A OSCG',
    'website': 'https://www.odoo-asia.com',
    'depends': [
        'purchase',
    ],
    'summary':"""""",
    'description': """
    """,
    'data': [
        'security/ir.model.access.csv',
        # 'views/res_country_views.xml',
        'views/supplier_location_views.xml',
        'views/supplier_stock_views.xml',
    ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
