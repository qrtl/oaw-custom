# -*- coding: utf-8 -*-
# Copyright 2017 Rooms For (Hong Kong) Limted T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_qty_in(self, prod_tmpl_id):
        res = 0.0
        moves = self.search([
            ('product_tmpl_id', '=', prod_tmpl_id),
            ('picking_type_code', '=', 'incoming'),
            ('state', '=', 'assigned'),
        ])
        for m in moves:
            res += m.product_uom_qty
        return res

    @api.multi
    def _update_prod_tmpl_local_atp(self):
        for move in self:
            prod_tmpl = move.product_tmpl_id
            qty_in = self._get_qty_in(prod_tmpl.id)
            prod_tmpl.qty_local_atp = int(prod_tmpl.qty_available + qty_in)
        return

    @api.multi
    def write(self, vals):
        res = super(StockMove, self).write(vals)
        self._update_prod_tmpl_local_atp()
        return res
