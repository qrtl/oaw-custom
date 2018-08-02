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
    @api.depends('quant_ids', 'reserved_quant_ids')
    def get_related_user(self):
        for move in self:
            quant_owner_id = False
            if move.quant_ids:
                quant_owner_id = move.quant_ids[0].owner_id
            elif move.reserved_quant_ids:
                quant_owner_id = move.reserved_quant_ids[0].owner_id
            if quant_owner_id and quant_owner_id.user_ids:
                move.related_user = quant_owner_id.user_ids[0].id
