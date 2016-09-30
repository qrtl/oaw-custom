# -*- coding: utf-8 -*-
# Copyright 2016 Rooms For (Hong Kong) Limited T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class stock_return_picking(osv.osv_memory):
    _inherit = 'stock.return.picking'

    # below is hook method
    def _get_move_hook(self, cr, uid, ids, data_get, new_qty, new_picking, pick_type_id, move_dest_id, context=None):
        record_id = context and context.get('active_id', False) or False
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('stock.picking')
        # uom_obj = self.pool.get('product.uom')
        # data_obj = self.pool.get('stock.return.picking.line')
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        data = self.read(cr, uid, ids[0], context=context)

        move = data_get.move_id #oscg
        vals = {
                    'product_id': data_get.product_id.id,
                    'product_uom_qty': new_qty,
                    'product_uos_qty': new_qty * move.product_uos_qty / move.product_uom_qty,
                    'picking_id': new_picking,
                    'state': 'draft',
                    'location_id': move.location_dest_id.id,
                    'location_dest_id': move.location_id.id,
                    'picking_type_id': pick_type_id,
                    'warehouse_id': pick.picking_type_id.warehouse_id.id,
                    'origin_returned_move_id': move.id,
                    'procure_method': 'make_to_stock',
                    'restrict_lot_id': data_get.lot_id.id,
                    'move_dest_id': move_dest_id,
                }
        if data['return_category'] == 'repair':
            repair_loc_id = self.pool.get('stock.location').search(cr, uid, [('is_repaired_location', '=', True)], context=context)
            if repair_loc_id:
                vals.update(location_dest_id = repair_loc_id[0])
        if move.picking_id.owner_id:
            vals['restrict_partner_id'] = move.picking_id.owner_id.id
        return move_obj.copy(cr, uid, move.id, vals)

    def _create_returns(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('stock.picking')
        uom_obj = self.pool.get('product.uom')
        data_obj = self.pool.get('stock.return.picking.line')
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        data = self.read(cr, uid, ids[0], context=context)
        returned_lines = 0

        # Cancel assignment of existing chained assigned moves
        moves_to_unreserve = []
        for move in pick.move_lines:
            to_check_moves = [move.move_dest_id] if move.move_dest_id.id else []
            while to_check_moves:
                current_move = to_check_moves.pop()
                if current_move.state not in ('done', 'cancel') and current_move.reserved_quant_ids:
                    moves_to_unreserve.append(current_move.id)
                split_move_ids = move_obj.search(cr, uid, [('split_from', '=', current_move.id)], context=context)
                if split_move_ids:
                    to_check_moves += move_obj.browse(cr, uid, split_move_ids, context=context)

        if moves_to_unreserve:
            move_obj.do_unreserve(cr, uid, moves_to_unreserve, context=context)
            #break the link between moves in order to be able to fix them later if needed
            move_obj.write(cr, uid, moves_to_unreserve, {'move_orig_ids': False}, context=context)

        #Create new picking for returned products
        pick_type_id = pick.picking_type_id.return_picking_type_id and pick.picking_type_id.return_picking_type_id.id or pick.picking_type_id.id
        new_picking = pick_obj.copy(cr, uid, pick.id, {
            'move_lines': [],
            'picking_type_id': pick_type_id,
            'state': 'draft',
            'origin': pick.name,
        }, context=context)

        for data_get in data_obj.browse(cr, uid, data['product_return_moves'], context=context):
            move = data_get.move_id
            if not move:
                raise osv.except_osv(_('Warning !'), _("You have manually created product lines, please delete them to proceed"))
            new_qty = data_get.quantity
            if new_qty:
                # The return of a return should be linked with the original's destination move if it was not cancelled
                if move.origin_returned_move_id.move_dest_id.id and move.origin_returned_move_id.move_dest_id.state != 'cancel':
                    move_dest_id = move.origin_returned_move_id.move_dest_id.id
                else:
                    move_dest_id = False

                returned_lines += 1

                self._get_move_hook(cr, uid, ids, data_get, new_qty, new_picking, pick_type_id, move_dest_id, context=context)#oscg
                #move_obj.copy(cr, uid, move.id, {#oscg
                #    'product_id': data_get.product_id.id,
                #    'product_uom_qty': new_qty,
                #    'product_uos_qty': new_qty * move.product_uos_qty / move.product_uom_qty,
                #    'picking_id': new_picking,
                #    'state': 'draft',
                #    'location_id': move.location_dest_id.id,
                #    'location_dest_id': move.location_id.id,
                #    'picking_type_id': pick_type_id,
                #    'warehouse_id': pick.picking_type_id.warehouse_id.id,
                #    'origin_returned_move_id': move.id,
                #    'procure_method': 'make_to_stock',
                #    'restrict_lot_id': data_get.lot_id.id,
                #    'move_dest_id': move_dest_id,
                #})

        if not returned_lines:
            raise osv.except_osv(_('Warning!'), _("Please specify at least one non-zero quantity."))

        pick_obj.action_confirm(cr, uid, [new_picking], context=context)
        pick_obj.action_assign(cr, uid, [new_picking], context)
        return new_picking, pick_type_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
