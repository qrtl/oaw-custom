# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Supplier Stock',
    'category': 'Stock',
    'version': '12.0.1.0.0',
    'author': 'Quartile Limited',
    'website': 'https://www.quartile.co',
    'depends': [
        'purchase',
        'mail',
        'stock',
    ],
    'summary':"""""",
    'description': """
    """,
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/supplier_location_views.xml',
        'views/supplier_stock_views.xml',
    ],
    'installable': True,
}
