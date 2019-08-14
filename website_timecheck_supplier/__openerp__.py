# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Website Timecheck Function For Supplier',
    'category': 'Website',
    'version': '8.0.1.0.0',
    'author': 'Quartile Limited',
    'website': 'https://www.quartile.co',
    'depends': [
        'website_timecheck',
        'website_category_responsive',
        'website_multi_image_zoom',
    ],
    'summary': """""",
    'description': """
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/supplier_stock_views.xml',
        'views/templates.xml',
    ],
    'installable': True,
}
