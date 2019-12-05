# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Quant/Serial Number on Purchase",
    "category": "Purchase",
    "summary": """""",
    "version": "12.0.1.0.0",
    "author": "Quartile Limited",
    "website": "https://www.quartile.co",
    "depends": ["vendor_consignment_stock", "sale_order_line_quant", "sale_view_adjust_oaw"],
    "description": """
- Add Quant to purchase order line.
- Overwrite _run_buy logic to create purhcase order based on supplier and
purchase currency.
    """,
    "data": ["views/purchase_order_views.xml", "views/sale_order_views.xml"],
}
