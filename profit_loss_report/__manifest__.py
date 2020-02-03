# Copyright 2020 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Profit and Loss Report",
    "version": "12.0.1.0.0",
    "author": "Quartile Limited",
    "website": "https://www.quartile.co",
    "category": "Report",
    "depends": [
        "account_invoice_paid_date_currency",
        "sale_order_line_quant",
    ],
    "description": """
    """,
    "data": [
        "security/ir.model.access.csv",
        "views/profit_loss_report_views.xml",
        "wizards/profit_loss_report_wizard_views.xml",
    ],
    "installable": True,
}
