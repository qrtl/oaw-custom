# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Partner Statement Report',
    'version': '8.0.2.0.0',
    'author': 'Quartile Limited',
    'website': 'https://www.odoo-asia.com',
    'category': 'Report',
    'depends': [
        'account_financial_report_webkit',
        'account_financial_report_webkit_xls',
    ],
    'description': """
    """,
    'data': [
        'views/account_config_settings_views.xml',
        'wizards/partner_statement_report_wizard_view.xml',
    ],
    'post_init_hook': '_update_account_move_line',
    'installable': True,
}
