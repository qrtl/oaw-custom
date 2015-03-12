# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) Rooms For (Hong Kong) Limited T/A OSCG. All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from datetime import datetime

from openerp import models, fields, api, _
from openerp.exceptions import Warning

class stock_transfer_details(models.TransientModel):
    _inherit = 'stock.transfer_details'
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(stock_transfer_details, self).default_get(cr, uid, fields, context=context)
        picking_ids = context.get('active_ids', [])
        active_model = context.get('active_model')

        if not picking_ids or len(picking_ids) != 1:
            # Partial Picking Processing may only be done for one picking at a time
            return res
        assert active_model in ('stock.picking'), 'Bad context propagation'
        picking_id, = picking_ids
        picking = self.pool.get('stock.picking').browse(cr, uid, picking_id, context=context)
        items = []
        packs = []
        if not picking.pack_operation_ids:
            picking.do_prepare_partial()
        for op in picking.pack_operation_ids:
            item = {
                'packop_id': op.id,
                'product_id': op.product_id.id,
                'product_uom_id': op.product_uom_id.id,
                'quantity': op.product_qty,
                'package_id': op.package_id.id,
                'lot_id': op.lot_id.id,
                'sourceloc_id': op.location_id.id,
                'destinationloc_id': op.location_dest_id.id,
                'result_package_id': op.result_package_id.id,
                'date': op.date, 
                'owner_id': op.owner_id.id,
                'invoice_state': op.invoice_state, #probuse
                'purchase_line_id': op.purchase_line_id.id, #probuse
                'move_dest_id': op.move_dest_id.id, #probuse
                'sale_line_id': op.sale_line_id.id, #probuse
            }
            if op.product_id:
                items.append(item)
            elif op.package_id:
                packs.append(item)
        res.update(item_ids=items)
        res.update(packop_ids=packs)
        return res
    
    @api.one
    def do_detailed_transfer(self):
        processed_ids = []
        # Create new and update existing pack operations
        for lstits in [self.item_ids, self.packop_ids]:
            for prod in lstits:
                
                if prod.invoice_state and prod.invoice_state != 'paid':#probuse
                    raise Warning(_('Warning'), _('You can not transfer the product since some of the lines payment has not been done.'))#probuse
                
                if prod.purchase_line_id:#probuse
                    prod.purchase_line_id.write({'lot_id':prod.lot_id.id })#probuse
                    prod.purchase_line_id.invoice_lines.write({'lot_id':prod.lot_id.id}) #probuse # Write on specific invoice line respected to purchase line with same lot number.

                if prod.sale_line_id:#probuse
                    prod.sale_line_id.write({'lot_id':prod.lot_id.id })#probuse
                
                if prod.move_dest_id:#probuse
                    prod.move_dest_id.write({'lot_id':prod.lot_id.id })#probuse
                
                pack_datas = {
                    'product_id': prod.product_id.id,
                    'product_uom_id': prod.product_uom_id.id,
                    'product_qty': prod.quantity,
                    'package_id': prod.package_id.id,
                    'lot_id': prod.lot_id.id,
                    'location_id': prod.sourceloc_id.id,
                    'location_dest_id': prod.destinationloc_id.id,
                    'result_package_id': prod.result_package_id.id,
                    'date': prod.date if prod.date else datetime.now(),
                    'owner_id': prod.owner_id.id,
                }
                if prod.packop_id:
                    prod.packop_id.write(pack_datas)
                    processed_ids.append(prod.packop_id.id)
                else:
                    pack_datas['picking_id'] = self.picking_id.id
                    packop_id = self.env['stock.pack.operation'].create(pack_datas)
                    processed_ids.append(packop_id.id)
        # Delete the others
        packops = self.env['stock.pack.operation'].search(['&', ('picking_id', '=', self.picking_id.id), '!', ('id', 'in', processed_ids)])
        for packop in packops:
            packop.unlink()

        # Execute the transfer of the picking
        self.picking_id.do_transfer()

        return True
    
class stock_transfer_details_items(models.TransientModel):
    _inherit = 'stock.transfer_details_items'
    
    invoice_state = fields.Char('Invoice State')#to stop the transfer if that move has not been paid by customer for case "On Delivery (per SO Line)"
    purchase_line_id = fields.Many2one('purchase.order.line',string="PO Line")
    sale_line_id = fields.Many2one('sale.order.line',string="SO Line")
    move_dest_id = fields.Many2one('stock.move',string="Destination Move")
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
