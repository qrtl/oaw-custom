# Copyright 2020  Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    subtotal_hkd = fields.Float(
        string="Subtotal in HKD",
        digits=dp.get_precision("Product Price"),
        readonly=True,
        store=True,
    )
    pricelist = fields.Many2one(
        related="order_id.pricelist_id", string="Pricelist", readonly=True
    )
