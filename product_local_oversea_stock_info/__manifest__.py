# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Product Offer',
    'version': '12.0.1.0.0',
    'author': 'Quartile Limited',
    'website': 'https://www.quartile.co',
    'category': 'Product',
    'depends': [
        'product',
        'sale_stock',
        'supplier_stock',
    ],
    'description': """
    """,
    'data': [
        'data/ir_actions.xml',
        'views/product_template_views.xml',
    ],
    'installable': True,
}
