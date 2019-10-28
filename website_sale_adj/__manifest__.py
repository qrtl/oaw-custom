# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Website Sales Adjustment',
    'version': '12.0.1.0.0',
    'author': 'Quartile Limited',
    'website': 'https://www.quartile.co',
    'category': 'Website',
    'license': "AGPL-3",
    'description': """
This module modify the website_sale module and provide following feature(s):
1. Hide the Add to Cart button
2. Add stock information to /shop page
    """,
    'summary': "",
    'depends': [
        'website_sale',
    ],
    'data': [
        'views/res_config_settings_views.xml',
        'views/templates.xml',
    ],
    'installable': True,
}
