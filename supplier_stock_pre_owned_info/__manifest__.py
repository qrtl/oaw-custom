# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": "Pre-Owned Products Features",
    "version": "12.0.1.0.1",
    "category": "Stock",
    "author": "Quartile Limited",
    "website": "https://www.quartile.co",
    "license": "LGPL-3",
    "depends": [
        "supplier_user_access"
    ],
    "data": [
        "data/product_condition_data.xml",
        "data/product_parts_status_data.xml",
        "security/ir.model.access.csv",
        "views/supplier_stock_views.xml",
    ],
    "installable": True,
}
