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
    price_unit = fields.Float(
        'Unit Price',
        digits=dp.get_precision('Product Price'),
        compute='_compute_price_unit',
        store=True,
    )

    @api.multi
    @api.depends('purchase_price_unit', 'exchange_rate')
    def _compute_price_unit(self):
        for lot in self:
            if lot.purchase_price_unit and lot.exchange_rate:
                lot.price_unit = lot.purchase_price_unit / lot.exchange_rate
