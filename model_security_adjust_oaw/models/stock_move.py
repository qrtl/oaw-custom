# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    quant_owner_related_user_id = fields.Many2one(
        comodel_name="res.users",
        compute="get_quant_owner_related_user_id",
        store=True,
    )
    supplier_pick_partner = fields.Char(
        string="Pick Partner",
        compute="get_supplier_pick_partner",
    )

    @api.multi
    @api.depends('quant_ids', 'reserved_quant_ids', 'quant_owner_id.user_ids')
    def get_quant_owner_related_user_id(self):
        for move in self:
            quant_owner_id = False
            if move.quant_ids:
                quant_owner_id = move.quant_ids[0].original_owner_id
            elif move.reserved_quant_ids:
                quant_owner_id = move.reserved_quant_ids[0].original_owner_id
            if quant_owner_id and quant_owner_id.sudo().user_ids:
                move.quant_owner_related_user_id = quant_owner_id.sudo().user_ids[0].id

    @api.multi
    def get_supplier_pick_partner(self):
        for move in self:
            if move.pick_partner_id.sudo().related_partner and \
                    move.pick_partner_id.sudo().related_partner == \
                    self.env.user.partner_id:
                move.supplier_pick_partner = move.pick_partner_id.sudo().name
            else:
                move.supplier_pick_partner = \
                    self.env['ir.config_parameter'].get_param(
                'default_supplier_pick_partner')
