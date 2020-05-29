# Copyright 2019-2020 chrono123 & Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": "Product List Price Update List View",
    "version": "12.0.1.1.0",
    "license": "LGPL-3",
    "author": "Quartile Limited",
    "website": "https://www.quartile.co",
    "category": "Product",
    "depends": ["product_local_oversea_stock_info", "product_offer_kanban_views"],
    "data": [
        "data/ir_actions.xml",
        "views/product_product_views.xml",
        "views/supplier_stock_views.xml",
    ],
    "installable": True,
}
