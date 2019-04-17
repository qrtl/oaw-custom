# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock VCI Revaluation",
    "version": "8.0.1.1.0",
    "category": "Stock",
    "website": "https://www.odoo-asia.com/",
    "author": "Quartile Limited",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "sale_line_quant_extended",
    ],
    "data": [
        "wizards/stock_vci_revaluation_wizard_view.xml",
        "data/stock_vci_revaluation_data.xml",
    ],
}
