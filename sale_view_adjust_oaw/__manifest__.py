# Copyright 2019 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sales View Adjust OAW",
    "summary": "",
    "version": "12.0.1.0.0",
    "category": "Sales",
    "author": "Quartile Limited",
    "website": "https://www.quartile.co",
    "description": """
    """,
    "license": "AGPL-3",
    "depends": [
        # 'web_tree_image',
        "sale_order_line_quant",
        "sale_margin",
    ],
    "data": ["data/ir_actions.xml", "views/sale_order_views.xml"],
}
