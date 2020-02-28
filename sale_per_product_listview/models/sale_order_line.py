# Copyright 2020  Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    subtotal_hkd = fields.Float(
        string="Subtotal in HKD",
        digits=dp.get_precision('Product Price'),
        readonly=True,
        store=True
    )
