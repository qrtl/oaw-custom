# Copyright 2019 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    quant_id = fields.Many2one("stock.quant", string="Stock Quant", copy=False)
    lot_id = fields.Many2one("stock.production.lot", string="Case No.", copy=False)
