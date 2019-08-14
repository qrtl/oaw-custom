# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Product Update Date',
    'version': '8.0.1.1.0',
    'author': 'Quartile Limited',
    'website': 'https://www.odoo-asia.com',
    'category': 'Product',
    'depends': [
        "product_listprice_list_view",
        "oa_product_update_filter"
    ],
    'description': """
    """,
    'data': [
        'views/product_template_views.xml',
        'views/product_product_views.xml',
        'views/supplier_stock_views.xml',
    ],
    'installable': True,
}
