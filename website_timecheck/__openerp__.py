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
        'oa_product_update_filter',
        'website_sale',
        'website_sale_adj',
        'website_multi_image_zoom',
        'website_sale_login_required',
    ],
    'summary':"""""",
    'description': """
    """,
    'data': [
        'data/ir_actions.xml',
        'reports/sale_order_reports.xml',
        'security/timecheck_security.xml',
        'security/website_sale_security.xml',
        'views/sale_order_views.xml',
        'views/templates.xml',
        'views/website_views.xml',
    ],
    'installable': True,
}
