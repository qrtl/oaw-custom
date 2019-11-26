# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Invoice Paid Date Currency",
    "version": "12.0.1.0.0",
    "category": "Account",
    "summary": "Add paid date and currency to account invoice",
    "description": """
This module will add a date to account invoice that capture the date that the
invoice is fully paid.
    """,
    "author": "Quartile Limited",
    "website": "http://www.quartile.co",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": ["views/account_invoice_views.xml"],
    "installable": True,
    "auto_install": False,
    "application": False,
}
