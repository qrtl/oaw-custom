# Copyright 2020 Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "quotation_reoprt_adjust",
    "summary": """
        Timeware specific reports""",
    "description": """
        Creates quotation, invoice, move reports for
        - Chrono123
        - Timeware
        - Sino
        Adds report relevant fields and logic:
        - partner note
        - Code (Quoation name and Customer Name
    """,
    "author": "Timeware Limited",
    "website": "http://www.yourcompany.com",
    "category": "Reports",
    "version": "12.0.0.1",
    "depends": ["base", "sale"],
    "data": [
        "views/quotation_report.xml",
        "views/quotation_report_timeware.xml",
        "views/sale_order_form.xml",
        "views/quotation_report_sino.xml",
    ],
    "demo": [],
}
