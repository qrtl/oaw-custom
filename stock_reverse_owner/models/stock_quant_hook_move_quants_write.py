# -*- coding: utf-8 -*-
# Copyright 2016 Rooms For (Hong Kong) Limited T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, SUPERUSER_ID
from openerp.addons.stock.stock import stock_quant


def move_quants_write(self, cr, uid, quants, move, location_dest_id,
                      dest_package_id, context=None):
    context = context or {}
    vals = {'location_id': location_dest_id.id,
            'history_ids': [(4, move.id)],
            'reservation_id': False}
    # >>> OSCG
    owner_id = False
    if location_dest_id.usage == 'internal':
        picking = move.picking_id
        owner_id = picking.owner_id and picking.owner_id.id or False
        if owner_id:
            vals['owner_id'] = owner_id
    # <<< OSCG

    if not context.get('entire_pack'):
        vals.update({'package_id': dest_package_id})
    self.write(cr, SUPERUSER_ID, [q.id for q in quants], vals, context=context)

class StockQuantHookMoveQuantsWrite(models.AbstractModel):
    _name = 'stock.quant.hook.move.quants.write'
    _desctription = 'Provide hook point for move_quants_write method'

    def _register_hook(self, cr):
        stock_quant.move_quants_write = move_quants_write
        return super(StockQuantHookMoveQuantsWrite, self)._register_hook(cr)
