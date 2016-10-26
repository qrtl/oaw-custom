# -*- coding: utf-8 -*-
# Copyright 2016 Rooms For (Hong Kong) Limited T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Return Shipment Process',
    'summary': 'Ownership Change Return Shipment Process',
    'version': '8.0.1.2.0',
    'category': 'Warehouse',
    'website': 'https://www.odoo-asia.net',
    'author': 'Rooms For (Hong Kong) Limited T/A OSCG',
    'license': 'AGPL-3',
    'depends': [
        'stock_account',
        'sale_line_quant_extended',
    ],
    'description': """
        Improves process of return shipment by adding return category in
        reverse transfer wizard.
    """,
    'data': [
        'data/stock_data.xml',
        'data/update.xml',
        'views/stock_location_view.xml',
        'views/stock_picking_view.xml',
        'views/sale_order_view.xml',
        'wizard/stock_return_picking_view.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
