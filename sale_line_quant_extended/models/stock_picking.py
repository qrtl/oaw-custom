# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_mto = fields.Boolean(
        'Make to Order',
    )
    to_check = fields.Boolean(
        'To Be Checked',
    )
