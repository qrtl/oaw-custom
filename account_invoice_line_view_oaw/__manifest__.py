# Copyright 2019 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Invoice Line View OAW",
    "version": "12.0.1.0.0",
    "category": "Account",
    "summary": "Adds Invoice Line menu item",
    "description": """
Main Features
==================================================
* Add menu item Invoice Lines
* Captures exchange rates as of the invoice dates and shows the base currency\
 amounts in the output.

    """,
    "author": "Quartile Limited",
    "website": "http://www.quartile.co",
    "license": "AGPL-3",
    "depends": ["account", "sale_order_line_quant", "account_invoice_line_quant"],
    "data": ["views/account_invoice_line_views.xml"],
    "application": False,
}
