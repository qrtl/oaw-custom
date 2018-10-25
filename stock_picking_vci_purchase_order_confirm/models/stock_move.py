# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def action_assign(self):
        for move in self:
            if move.picking_id.sale_id and self.env.context.get('button_assign'):
                move.picking_id.sale_id.confirm_vci_purhcase_order()
        return super(StockMove, self).action_assign()
