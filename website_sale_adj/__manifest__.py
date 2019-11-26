# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Website Sales Adjustment",
    "version": "12.0.1.0.0",
    "author": "Quartile Limited",
    "website": "https://www.quartile.co",
    "category": "Website",
    "license": "AGPL-3",
    "description": """
This module modify the website_sale module and provide following feature(s):
1. Add "About Us", "Contact Information" and "Empty Shop Display Message" to website settings
2. Remove default design of footer, display "About Us", "Contact Information".
3. Show "Empty Shop Display Message" when the shop page return empty result.
    """,
    "summary": "",
    "depends": ["website_sale"],
    "data": ["views/res_config_settings_views.xml", "views/templates.xml"],
    "installable": True,
}
