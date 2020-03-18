# Copyright 2020 Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Product Sale List View",
    "summary": """
      Shows sales for each product. """,
    "description": """
        For each product a tree view that lists all sale order lines and total amount this product has generated.
        Sale Order Lines will be considered only - from the moment the quotation is turned into SO
        Refunded Sales Orders will not be considered.
    """,
    "author": "Quartile Limited, Timeware Limited",
    "category": "Product",
    "version": "12.0.1.0.0",
    "depends": ["product_local_oversea_stock_info"],
    "data": [
        "data/ir_actions.xml",
        "views/product_template_views.xml",
        "views/sale_order_line_views.xml",
    ],
    "installable": True,
}
