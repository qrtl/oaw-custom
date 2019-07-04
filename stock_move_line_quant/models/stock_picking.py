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
