# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    related_user = fields.Many2one(
        comomodel="res.partner",
        compute="get_related_user",
        store=True,
    )

    @api.multi
    @api.depends('quant_owner_id')
    def get_related_user(self):
        for move in self:
            if move.quant_owner_id and move.quant_owner_id.user_id:
                move.related_user = move.quant_owner_id.user_id[0].id
