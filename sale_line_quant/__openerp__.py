# -*- coding: utf-8 -*-
#    Odoo, Open Source Management Solution
#    Copyright (c) Rooms For (Hong Kong) Limited T/A OSCG. All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
{
    'name': 'Quant/Serial Number on Sales',
    'category': 'Sale',
    'version': '8.0.1.0.0',
    'author': 'Rooms For (Hong Kong) Ltd. T/A OSCG',
    'website': 'www.odoo-asia.com',
    'depends': ['sale', 'stock', 'sale_margin', 'vendor_consignment_stock',
                'sale_owner_stock_sourcing',],
    'summary':""" Serial Number Quant on Sales Order Line""",
    'description': """ 
Modification on sales order line by adding quant and serial number selection.
    """,
    'data': [
             'security/group.xml',
             'view/sale_view.xml',
             'view/purchase_view.xml',
             'view/stock_view.xml',
             'view/sale_stock_view.xml',
             'view/so_line_quant_view.xml',
             'view/account_invoice_view.xml',
             ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
