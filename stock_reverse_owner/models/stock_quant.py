# -*- coding: utf-8 -*-
# Copyright 2016 Rooms For (Hong Kong) Limited T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api

class stock_quant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def move_quants_write(self, quants, move, location_dest_id, dest_package_id):
        res = super(stock_quant, self).move_quants_write(quants, move,
                                                         location_dest_id,
                                                         dest_package_id)
        if location_dest_id.usage == 'internal':
            picking = move.picking_id
            quant_ids = [q.id for q in quants]
            quant_ids = self.browse(quant_ids)
            owner_id = picking.owner_id and picking.owner_id.id or False
            quant_ids.sudo().write({'owner_id': owner_id})
        return res


def move_quants_write(self, cr, uid, quants, move, location_dest_id,
                      dest_package_id, context=None):
    context = context or {}
    vals = {'location_id': location_dest_id.id,
            'history_ids': [(4, move.id)],
            'reservation_id': False}
    if not context.get('entire_pack'):
        vals.update({'package_id': dest_package_id})
    self.write(cr, SUPERUSER_ID, [q.id for q in quants], vals, context=context)
