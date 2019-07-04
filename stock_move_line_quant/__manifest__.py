# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Quant/Serial Number on Stock Move Line',
    'category': 'Stock',
    'version': '12.0.1.0.0',
    'author': 'Quartile Limited',
    'website': 'https://www.quartile.co',
    'depends': [
        'stock',
    ],
    'summary':"",
    'description': """ 
Add following purchase price fields to stock move line, pass the value to 
serial number and quant object when performing a receipt.
    """,
    'data': [
        'views/stock_move_line_views.xml',
        'views/stock_picking_views.xml',
        'views/stock_quant_views.xml',
    ],
    'installable': True,
}
