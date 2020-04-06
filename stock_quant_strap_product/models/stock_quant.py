# Copyright 2020 Quartile Limted
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    strap_product_id = fields.Many2one(string="Strap")
    strap_product_image = fields.Binary(
        related="strap_product_id.image_medium", string="Strap Image"
    )
