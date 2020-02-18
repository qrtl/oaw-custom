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
        Function of the Chrono24 Updated flag: This flag gets activated when product is to be pusblished onto Chrono24 or when changes 
        to certain fields in the master PLU view are done
    """,
    "data": ["data/ir_actions.xml",
        "views/product_product_views.xml",
             "views/product_template_views.xml",
     ],
    "qweb": [],
    "installable": True,
}
