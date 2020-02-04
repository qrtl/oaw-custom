# Copyright 2020  Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Adds chrono24 management to Sales ",
    "category": "Security",
    "version": "12.0.0.1",
    "author": "Quartile Limited, Timeware Limited.",
    "website": "",
    "depends": [
        "product",
        "product_local_oversea_stock_info",
        "product_listprice_list_view",
    ],
    "summary": """Adds chrono24  fields to PLV. Adds a new tree views to Sales to manage chrono24""",
    "description": """
        Function of the Chrono24 Updated flag: This flag gets activated by two mechanisms, either by changes done by sale manager or by using a More-button. 
    """,
    "data": ["views/product_product_views.xml", "data/ir_actions.xml"],
    "qweb": [],
    "installable": True,
}
