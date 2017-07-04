# -*- coding: utf-8 -*-
# Copyright 2015-2017 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Quant/Serial Number on Sales',
    'category': 'Sale',
    'version': '8.0.1.5.1',
    'author': 'Quartile Limited',
    'website': 'https://www.odoo-asia.com',
    'depends': [
        'stock',
        'sale_margin',
        'vendor_consignment_stock',
        'sale_owner_stock_sourcing',
        'account_invoice_refund_link',
    ],
    'summary':""" Serial Number Quant on Sales Order Line""",
    'description': """ 
Modification on sales order line by adding quant and serial number selection.
    """,
    'data': [
        'security/group.xml',
        'views/sale_view.xml',
        'views/purchase_view.xml',
        'views/stock_view.xml',
        'views/sale_stock_view.xml',
        'views/so_line_quant_view.xml',
        'views/account_invoice_view.xml',
    ],
    'installable': True,
}
