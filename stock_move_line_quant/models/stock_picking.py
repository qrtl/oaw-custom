# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    purchase_currency_id = fields.Many2one(
        'res.currency',
        string='Purchase Currency',
        default=lambda self: self.env.user.company_id.currency_id,
        states={'draft': [('readonly', False)]},
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Purchase Currency',
    )
    exchange_rate = fields.Float(
        'FX Rate',
        digits=(12, 6),
    )

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        if self.currency_id:
            self.exchange_rate = self.currency_id.rate
