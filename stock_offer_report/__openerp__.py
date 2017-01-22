# -*- coding: utf-8 -*-
# Copyright 2016-2017 Rooms For (Hong Kong) Limited T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock Offer Report",
    "summary": "",
    "version": "8.0.1.1.0",
    "category": "Reporting",
    "website": "https://www.odoo-asia.com/",
    "author": "Rooms For (Hong Kong) Limited T/A OSCG",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "sale_line_quant_extended",
        "stock_reverse_owner",
        "abstract_report_xlsx",
        "product_offer",
    ],
    "data": [
        "wizards/offer_report_wizard_view.xml",
        "menuitems.xml",
        "reports.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
