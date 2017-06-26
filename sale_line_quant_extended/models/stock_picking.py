# -*- coding: utf-8 -*-
# Copyright 2015-2017 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_mto = fields.Boolean(
        'Make to Order',
    )
    to_check = fields.Boolean(
        'To Be Checked',
    )
