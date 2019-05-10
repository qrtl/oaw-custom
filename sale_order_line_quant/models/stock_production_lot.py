# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    currency_id = fields.Many2one(
        'res.currency',
        string='Purchase Currency',
        readonly=True,
    )
    purchase_price_unit = fields.Float(
        string='Purchase Currency Price',
        digits_compute=dp.get_precision('Product Price'),
        readonly=True,
    )
    original_owner_id = fields.Many2one(
        'res.partner',
        string='Original Owner',
        readonly=True,
    )
    exchange_rate = fields.Float(
        'FX Rate',
        digits=(12, 6),
    )
