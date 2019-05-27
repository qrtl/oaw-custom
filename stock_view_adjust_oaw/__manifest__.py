# Copyright 2019 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Stock View Adjust',
    'version': '12.0.1.0.0',
    'category': 'Stock',
    'author': 'Quartile Limited',
    'website': 'https://www.quartile.co',
    'description': """
    """,
    "license": "AGPL-3",
    'depends': [
        'sale_order_line_quant',
        'stock_picking_menu',
    ],
    'data': [
        'data/ir_actions.xml',
        'views/stock_move_views.xml',
        'views/stock_quant_views.xml',
    ],
}
