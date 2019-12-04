# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Website Timecheck Function',
    'category': 'Website',
    'version': '8.0.1.0.0',
    'author': 'Quartile Limited',
    'website': 'https://www.quartile.co',
    'depends': [
        'model_security_adjust_oaw',
        'product_offer',
        'product_listprice_list_view',
        'supplier_stock_hk_location',
        'website_sale',
        'website_sale_adj',
        'website_multi_image_zoom',
    ],
    'summary': """""",
    'description': """
    """,
    'data': [
        'data/ir_actions.xml',
        'reports/sale_order_reports.xml',
        'security/timecheck_security.xml',
        'security/website_sale_security.xml',
        'views/account_invoice_views.xml',
        'views/product_product_views.xml',
        'views/sale_order_views.xml',
        'views/templates.xml',
        'views/website_views.xml',
    ],
    'installable': True,
    'qweb': [
        'static/src/xml/base.xml',
    ],
}
