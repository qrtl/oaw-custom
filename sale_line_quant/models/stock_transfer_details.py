# -*- coding: utf-8 -*-
# Copyright 2015-2017 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
                # 'invoice_state': op.invoice_state, # oscg
                'purchase_line_id': op.purchase_line_id.id, # oscg
                'move_dest_id': op.move_dest_id.id, # oscg
                'sale_line_id': op.sale_line_id.id, # oscg
            }
            if op.product_id:
                items.append(item)
            elif op.package_id:
                packs.append(item)
        res.update(item_ids=items)
        res.update(packop_ids=packs)
        return res

    @api.model
    def _update_related_records(self, rec, lot_id):
        invoice_lines = []
        rec.write({'lot_id': lot_id.id})
        if rec.invoice_lines:
            invoice_lines.append(rec.invoice_lines)
        # if rec is PO line, then try to update lot_id of related SO line
        # and customer invoice line(s) as well
        if rec._name == 'purchase.order.line':
            so_line = self.env['sale.order.line'].search(
                [('purchase_line_id', '=', rec.id)])
            if so_line:
                so_line.write({'lot_id': lot_id.id})
                if so_line.invoice_lines:
                    invoice_lines.append(so_line.invoice_lines)
        for line in invoice_lines:
            line.write({'lot_id': lot_id.id})
            rel_lines = self.env['account.invoice.line'].search(
                [('origin_invoice_line_id','=',line.id)])
            for rel_line in rel_lines:
                rel_line.write({'lot_id': lot_id.id})

    @api.one
    def do_detailed_transfer(self):
        processed_ids = []
        # Create new and update existing pack operations
        for lstits in [self.item_ids, self.packop_ids]:
            for prod in lstits:
                # >>> oscg
                if prod.sale_line_id and prod.sale_line_id.\
                    order_id.order_policy == 'line_check':
                    check_error = False
                    if not prod.sale_line_id.invoice_lines:
                        check_error = True
                    else:
                        for line in prod.sale_line_id.invoice_lines:
                            if line.invoice_id.state != 'paid':
                                check_error = True
                    if check_error:
                        raise Warning(_('Error!'), _('You cannot transfer the \
                            product due to unpaid SO line(s).'))
                if prod.purchase_line_id:
                    self._update_related_records(prod.purchase_line_id,
                                                 prod.lot_id)
                if prod.sale_line_id:
                    self._update_related_records(prod.sale_line_id,
                                                 prod.lot_id)
                if prod.move_dest_id:
                    prod.move_dest_id.write({'lot_id':prod.lot_id.id })
                # <<< oscg
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
