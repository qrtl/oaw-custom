# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class SupplierStock(models.Model):
    _inherit = "supplier.stock"

    product_condition_id = fields.Many2one("product.condition", string="Condition")
    product_parts_status_id = fields.Many2one("product.parts.status", string="Parts")
    warrant_status = fields.Selection(
        [
            ("empty", "Empty Date"),
            ("flexibile", "Will Fill Date By Sold"),
            ("fix", "Fixed Date"),
        ],
        string="Warrent Status",
    )
    warranty_date = fields.Date(string="Warranty Date")
