# Copyright 2019 Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Views Adjustments",
    "author": "Quartile Limited, Timeware Limted",
    "summary": "",
    "version": "12.0.1.0.0",
    "website": "https://www.ehanse.de",
    "category": "Accounting",
    "depends": ["sale", "account"],
    "description": """
- Adjust account payment views.
    """,
    "data": ["views/account_payment_views.xml",
             "views/account_move_views.xml"
             ],
    "installable": True,
}
