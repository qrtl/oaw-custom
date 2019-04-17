# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Hide chatter box from supplier',
    'category': 'Security',
    'version': '8.0.1.0.0',
    'author': 'Quartile Limited',
    'website': 'https://www.quartile.co',
    'depends': [
        'model_security_adjust_oaw',
    ],
    'summary':"""""",
    'description': """
    """,
    'data': [
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/product_template_views.xml',
    ],
    'installable': True,
}
