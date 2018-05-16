# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Model Security Adjust OAW',
    'category': 'Security',
    'version': '8.0.1.3.1',
    'author': 'Quartile Limited',
    'website': 'https://www.quartile.co',
    'depends': [
        'partner_statement_report',
        'stock_offer_report',
        'stock_consignment_report',
        'supplier_stock',
        'product'
    ],
    'summary':"""""",
    'description': """
    """,
    'data': [
        'security/supplier_security.xml',
        'security/base_security.xml',
        'security/ir.model.access.csv',
        'views/account_fiscalyear_views.xml',
        'views/advance_search_disable.xml',
        'views/stock_views.xml',
        'views/supplier_stock_views.xml',
        'wizards/consignment_report_wizard_view.xml',
        'wizards/partner_statement_report_wizard_view.xml',
    ],
    'post_init_hook': '_update_partner_offer_fields',
    'qweb': [
        'static/src/xml/base.xml',
    ],
    'installable': True,
}
