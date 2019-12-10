# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Quant/Serial Number on Sales",
    "category": "Sale",
    "version": "12.0.1.0.0",
    "author": "Quartile Limited",
    "website": "https://www.quartile.co",
    "depends": [
        "stock",
        "sale_margin",
        "stock_move_line_quant",
        "sale_owner_stock_sourcing",
    ],
    "summary": """ Serial Number Quant on Sales Order Line""",
    "description": """
Modification on sales order line by adding quant and serial number selection.
    """,
    "data": ["views/sale_order_views.xml"],
    "installable": True,
}
