# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Split Sales Order Lines',
    'category': 'Sale',
    'version': '12.0.1.0.0',
    'author': 'Quartile Limited',
    'website': 'https://www.quartile.co',
    'depends': [
        'sale',
    ],
    'summary': "",
    'description': """ 
Provide a button to split the sale order lines into qty 1.
    """,
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
}
