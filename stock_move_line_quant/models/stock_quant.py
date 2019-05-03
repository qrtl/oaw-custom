# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class StockQuant(models.Model):
    _inherit = "stock.quant"

    currency_id = fields.Many2one(
        related='lot_id.currency_id',
        string='Purchase Currency',
        store=True,
        readonly=True,
    )
    purchase_price_unit = fields.Float(
        related='lot_id.purchase_price_unit',
        string='Purchase Currency Price',
        digits_compute=dp.get_precision('Product Price'),
        store=True,
        readonly=True,
    )
    original_owner_id = fields.Many2one(
        related='lot_id.original_owner_id',
        string='Original Owner',
        store=True,
        readonly=True,
    )
    exchange_rate = fields.Float(
        related='lot_id.exchange_rate',
        string='FX Rate',
        digits=(12, 6),
        store=True,
        readonly=True,
    )
