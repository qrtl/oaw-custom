# Copyright 2020 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Website Timecheck Function",
    "category": "Website",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Quartile Limited",
    "website": "https://www.quartile.co",
    "depends": [
        "supplier_user_access",
        "product_listprice_list_view",
        "website_sale_adj",
    ],
    "summary": """""",
    "data": [
        "data/ir_actions.xml",
        "security/timecheck_security.xml",
        "security/website_sale_security.xml",
        "views/product_product_views.xml",
        "views/res_users_views.xml",
        "views/sale_order_views.xml",
        "views/templates.xml",
    ],
    "installable": True,
    "qweb": ["static/src/xml/base.xml"],
}
