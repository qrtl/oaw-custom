# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Retail Currency Update',
    'version': '12.0.1.0.0',
    'author': 'Quartile Limited',
    'website': 'https://www.quartile.co',
    'category': 'Product',
    'depends': [
        "sale",
        "stock",
    ],
    'description': """
* Adds a menu item 'Retail Currency Update' to facilitate list 
price (currency) update
    """,
    'data': [
        'views/product_template_views.xml',
    ],
    'installable': True,
}
