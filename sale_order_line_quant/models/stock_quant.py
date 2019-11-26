# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    sale_order_id = fields.Many2one(
        "sale.order", string="Related Sale Order", readonly=True
    )
