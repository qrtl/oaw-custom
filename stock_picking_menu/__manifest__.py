# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Stock Picking Menu',
    'version': '12.0.1.0.0',
    'author': 'Quartile Limited',
    'website': 'https://www.quartile.co',
    'category': 'stock',
    'description': """
* Adds menu items for users to reach picking operation screens quickly.
* Default proposal of Picking Type is for the first warehouse.
    """,
    'depends': [
        "stock"
    ],
    'data': [
        'views/stock_picking_views.xml',
    ],
    'installable': True,
}
