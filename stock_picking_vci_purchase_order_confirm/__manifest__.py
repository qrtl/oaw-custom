# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Check Availability button confirms VCI RFQ',
    'version': '8.0.1.0.0',
    'category': 'Stock',
    'description': """

    """,
    'author': 'Quartile Limited',
    'website': 'https://www.quartile.co',
    "license": "AGPL-3",
    'depends': [
        'stock',
        'sale',
        'sale_line_quant_extended'
    ],
    'data': [
        'views/stock_picking_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
