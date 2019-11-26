# Copyright 2019 chrono123 & Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product List Price Update List View",
    "version": "12.0.1.0.1",
    "author": "Quartile Limited",
    "website": "https://www.quartile.co",
    "category": "Product",
    "depends": ["product_local_oversea_stock_info", "product_offer_kanban_views"],
    "description": """
* Adds a menu item 'Product List Price Update' to facilitate list price update
    """,
    "data": ["views/product_product_views.xml", "views/supplier_stock_views.xml"],
    "installable": True,
}
