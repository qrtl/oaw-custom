# -*- coding: utf-8 -*-
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

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class stock_move(osv.osv):
    _inherit = 'stock.move'
    _columns = {
        'quant_id': fields.many2one('stock.quant', string="Quant from SO"),
        'lot_id': fields.many2one('stock.production.lot', string="Case No. \
            from SO"),
        'currency_id' : fields.many2one('res.currency', string='Purchase \
            Currency', required=False, readonly=False),
        'purchase_price_unit': fields.float('Purchase Currency Price',
            required=False, digits_compute= dp.get_precision('Product \
            Price')),
        'code': fields.related('picking_type_id', 'code', type='char',
            string='Type of Operation', readonly=True, store=True),
    }

    def onchange_picking_type(self, cr, uid, ids, picking_type_id, context=None):
        result = {}
        picktype_obj = self.pool.get('stock.picking.type')
        if picking_type_id:
            picktype_data = picktype_obj.browse(cr, uid, picking_type_id, context)
            result.update({'code': picktype_data.code})
        return {'value': result}

    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False,
            loc_dest_id=False, partner_id=False):
        res = super(stock_move, self).onchange_product_id(cr, uid, ids,
                prod_id, loc_id, loc_dest_id, partner_id)
        if 'value' in res:
            res['value'].update({'quant_id': False})
        return res
     
    def onchange_purchase_currency(self, cr, uid, ids, company_id, date,
        currency_id, purchase_price_unit, context=None):
        # reset the value of price_unit on stock.move if purchase price
        # currency of the move is updated
        result = {}
        if currency_id and purchase_price_unit:
            currency_obj = self.pool.get('res.currency')
            company_obj = self.pool.get('res.company')
            company_data = company_obj.browse(cr, uid, company_id, context)
            ctx = context.copy()
            ctx.update({'date': date})
            price_unit = currency_obj.compute(cr, uid, currency_id,
                company_data.currency_id.id, purchase_price_unit, context=ctx)
            result.update({'price_unit': price_unit})
        return {'value': result}
    
    # constraint
    def _check_purchase_with_poref(self, cr, uid, ids, context=None):
        # prevent user from changing price/currency in case of receipt with PO
        # reference
        for move in self.browse(cr, uid, ids, context=context):
            if move.picking_type_id.code == 'incoming' \
                and move.purchase_line_id \
                and (move.currency_id \
                     or move.purchase_price_unit != 0.0):
                return False
        return True

    def _check_purchase_without_poref(self, cr, uid, ids, context=None):# Constraint
        # raise error if user tries to create stock move without purchase
        # price and its currency in case of receipt created without PO ref.
        """ exclude the case source location customer (= customer return) """
        for move in self.browse(cr, uid, ids, context=context):
            if move.picking_id.picking_type_id.code == 'incoming' \
                and move.location_id.usage != 'customer' \
                and not move.purchase_line_id \
                and (not move.currency_id \
                     or move.purchase_price_unit < 0):
                return False
        return True
        
    _constraints = [
         (_check_purchase_with_poref, 'Error! You are not allowed to update \
             purchase price if the receipt refers to a purchase order.',
             ['currency_id', 'purchase_price_unit']),
         (_check_purchase_without_poref, 'Error! Purchase price must be \
             provided.', ['currency_id', 'purchase_price_unit'])
         ]

    def _get_invoice_line_vals(self, cr, uid, move, partner, inv_type, context=None):
        res = super(stock_move, self)._get_invoice_line_vals(cr, uid, move, partner, inv_type, context=context)
        # Pass the lot reference if invoice created from pickings.
        res.update({'lot_id': move.lot_id.id})
        return res
    
    def action_assign(self, cr, uid, ids, context=None):
        """ Checks the product type and accordingly writes the state.
        """
        
        #NEED TO OVERRIDE COMPLETE METHOD SINCE LOGIC WAS INBETWEEN THE LINES. PLEASE CHECK TAG #oscg TAG FOR CHANGES DONE ON THIS.
        
        context = context or {}
        quant_obj = self.pool.get("stock.quant")
        to_assign_moves = []
        main_domain = {}
        todo_moves = []
        operations = set()
        for move in self.browse(cr, uid, ids, context=context):
            if move.state not in ('confirmed', 'waiting', 'assigned'):
                continue
            if move.location_id.usage in ('supplier', 'inventory', 'production'):
                to_assign_moves.append(move.id)
                #in case the move is returned, we want to try to find quants before forcing the assignment
                if not move.origin_returned_move_id:
                    continue
            if move.product_id.type == 'consu':
                to_assign_moves.append(move.id)
                continue
            else:
                todo_moves.append(move)

                #we always keep the quants already assigned and try to find the remaining quantity on quants not assigned only
                main_domain[move.id] = [('reservation_id', '=', False), ('qty', '>', 0)]

                #if the move is preceeded, restrict the choice of quants in the ones moved previously in original move
                ancestors = self.find_move_ancestors(cr, uid, move, context=context)
                if move.state == 'waiting' and not ancestors:
                    #if the waiting move hasn't yet any ancestor (PO/MO not confirmed yet), don't find any quant available in stock
                    main_domain[move.id] += [('id', '=', False)]
                elif ancestors:
                    main_domain[move.id] += [('history_ids', 'in', ancestors)]

                #if the move is returned from another, restrict the choice of quants to the ones that follow the returned move
                if move.origin_returned_move_id:
                    main_domain[move.id] += [('history_ids', 'in', move.origin_returned_move_id.id)]
                for link in move.linked_move_operation_ids:
                    operations.add(link.operation_id)
        # Check all ops and sort them: we want to process first the packages, then operations with lot then the rest
        operations = list(operations)
        operations.sort(key=lambda x: ((x.package_id and not x.product_id) and -4 or 0) + (x.package_id and -2 or 0) + (x.lot_id and -1 or 0))
        for ops in operations:
            #first try to find quants based on specific domains given by linked operations
            for record in ops.linked_move_operation_ids:
                move = record.move_id
                if move.id in main_domain:
                    domain = main_domain[move.id] + self.pool.get('stock.move.operation.link').get_specific_domain(cr, uid, record, context=context)
                    qty = record.qty
                    if qty:
                    # add a serial number field in SO line, which should be passed to delivery order 
                    # to reserve a quant of the selected serial number                        
                        if record.move_id.quant_id: #oscg
                            quants = [(record.move_id.quant_id, record.move_id.quant_id.qty)] #oscg
                        else: #oscg
                            quants = quant_obj.quants_get_prefered_domain(cr,
                                uid, ops.location_id, move.product_id, qty,
                                domain=domain, prefered_domain_list=[],
                                restrict_lot_id=move.restrict_lot_id.id,
                                restrict_partner_id=move.restrict_partner_id.\
                                id, context=context) #oscg
                            
                        quant_obj.quants_reserve(cr, uid, quants, move, record, context=context)
        for move in todo_moves:
            if move.linked_move_operation_ids:
                continue
            # then if the move isn't totally assigned, try to find quants without any specific domain
            if move.state != 'assigned':
                qty_already_assigned = move.reserved_availability
                qty = move.product_qty - qty_already_assigned
                
                # add a serial number field in SO line, which should be passed to delivery order 
                # to reserve a quant of the selected serial number
                if move.quant_id: #oscg
                    quants = [(move.quant_id, qty)] #oscg
                else: #oscg
                    quants = quant_obj.quants_get_prefered_domain(cr, uid,
                        move.location_id, move.product_id, qty,
                        domain=main_domain[move.id], prefered_domain_list=[],
                        restrict_lot_id=move.restrict_lot_id.id,
                        restrict_partner_id=move.restrict_partner_id.id,
                        context=context) #oscg
                
#                 a = self.pool.get('stock.move').read(cr,uid,move.id)
                quant_obj.quants_reserve(cr, uid, quants, move, context=context)

        #force assignation of consumable products and incoming from supplier/inventory/production
        if to_assign_moves:
            self.force_assign(cr, uid, to_assign_moves, context=context)
            
    def _prepare_procurement_from_move(self, cr, uid, move, context=None):
        res = super(stock_move, self)._prepare_procurement_from_move(cr, uid, move, context=context)
        # Pass the lot ref, to stock move.
        res.update({'lot_id': move.lot_id.id})
        return res


class stock_quant(osv.osv):
    _inherit = "stock.quant"

    def _actual_qty(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for quant in self.browse(cr, uid, ids, context=context):
            res[quant.id] = quant.qty - quant.sale_reserver_qty
        return res
    
    def _get_quant_name(self, cr, uid, ids, name, args, context=None):
        return super(stock_quant, self)._get_quant_name(cr, uid, ids, name, args, context=context)
    
    _description = "Stock Quants"
    _columns = {
        # make 'name' a stored field for searching purpose in SO line
        'name': fields.function(_get_quant_name, type='char',
            store={'stock.quant': (lambda self, cr, uid, ids, c={}: ids, [], 10)},
            string='Identifier'),
        'usage': fields.related('location_id', 'usage', type='char', string='Type of Location', readonly=True, store=True),
        'sale_reserver_qty': fields.related('reservation_id',
            'product_uom_qty', type='float', string='Sale Reserved Quantity',
            readonly=True, store=True),
        'actual_qty': fields.function(_actual_qty, string='Actual Quantity', help="It is: Quantity - Sale Reserved Quantity", type='float', store={
                'stock.quant': (lambda self, cr, uid, ids, c={}: ids, [], 10),
            },),
        'currency_id' : fields.many2one('res.currency', string='Purchase \
            Currency', required=False, readonly=True),
        'purchase_price_unit': fields.float('Purchase Currency Price',
            required=False, digits_compute= dp.get_precision('Product Price'),
            readonly=True),
    }
    
    def _quant_create(self, cr, uid, qty, move, lot_id=False, owner_id=False,
        src_package_id=False, dest_package_id=False,
        force_location_from=False, force_location_to=False, context=None):
        quant = super(stock_quant, self)._quant_create(cr, uid, qty, move,
            lot_id, owner_id, src_package_id, dest_package_id,
            force_location_from, force_location_to, context)
        self.write(cr, uid, [quant.id],
            {'currency_id': move.currency_id.id,
            'purchase_price_unit': move.purchase_price_unit},
            context)
        return quant

    # this is to update 'name' field at installation/upgrade
    def init(self, cr):
        quant_ids = self.search(cr, SUPERUSER_ID, [])
        self.write(cr, SUPERUSER_ID, quant_ids, {})


class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'
    
    def _check_serial_enforce(self, cr, uid, ids, context=None):
        #i. Serial number + product should be unique in serial number master (stock.product.lot) 
        for prod in self.browse(cr, uid, ids, context=context):
            if prod.product_id.product_tmpl_id.categ_id.enforce_qty_1:
                lot_ids = self.search(cr, uid, [('id', '!=', prod.id),('product_id', '=', prod.product_id.id),('name', '=', prod.name)])
                if lot_ids:
                    return False
        return True 
    
    def _check_serial_qty(self, cr, uid, ids, context=None):
        # Qty on hand should not exceed 1 for serial number + product
        for prod in self.browse(cr, uid, ids, context=context):
            if prod.product_id.product_tmpl_id.categ_id.enforce_qty_1:
                if prod.lot_balance > 1:
                    return False
        return True
        
    _constraints = [
        (_check_serial_enforce, 'Error! Serial number must be unique for \
            product with "ENFORCE QTY 1" setting.', ['name', 'product_id']),
        (_check_serial_qty, 'Error! Quantity on hand should not exceed 1 for \
            product with "ENFORCE QTY 1" setting.', ['lot_balance'])
    ]


class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    
    def _prepare_pack_ops(self, cr, uid, picking, quants, forced_qties, context=None):
        """ returns a list of dict, ready to be used in create() of stock.pack.operation.

        :param picking: browse record (stock.picking)
        :param quants: browse record list (stock.quant). List of quants associated to the picking
        :param forced_qties: dictionary showing for each product (keys) its corresponding quantity (value) that is not covered by the quants associated to the picking
        """
        
        if picking.origin:
            sale_obj = self.pool.get('sale.order')
            sale_ids = sale_obj.search(cr, uid, [('name', '=', picking.origin)])
            if sale_ids:
                sale = sale_obj.browse(cr, uid, sale_ids[0])
                if not sale.is_enforce_qty:
                    return super(stock_picking, self)._prepare_pack_ops(cr, uid, picking, quants, forced_qties, context=context)
        
        def _picking_putaway_apply(product):
            location = False
            # Search putaway strategy
            if product_putaway_strats.get(product.id):
                location = product_putaway_strats[product.id]
            else:
                location = self.pool.get('stock.location').get_putaway_strategy(cr, uid, picking.location_dest_id, product, context=context)
                product_putaway_strats[product.id] = location
            return location or picking.location_dest_id.id

        # If we encounter an UoM that is smaller than the default UoM or the one already chosen, use the new one instead.
        product_uom = {} # Determines UoM used in pack operations
        for move in picking.move_lines:
            if not product_uom.get(move.product_id.id):
                product_uom[move.product_id.id] = move.product_id.uom_id
            if move.product_uom.id != move.product_id.uom_id.id and move.product_uom.factor > product_uom[move.product_id.id].factor:
                product_uom[move.product_id.id] = move.product_uom

        pack_obj = self.pool.get("stock.quant.package")
        quant_obj = self.pool.get("stock.quant")
        vals = []
        qtys_grouped = {}
        #for each quant of the picking, find the suggested location
        quants_suggested_locations = {}
        product_putaway_strats = {}
        for quant in quants:
            if quant.qty <= 0:
                continue
            suggested_location_id = _picking_putaway_apply(quant.product_id)
            quants_suggested_locations[quant] = suggested_location_id

        #find the packages we can movei as a whole
        top_lvl_packages = self._get_top_level_packages(cr, uid, quants_suggested_locations, context=context)
        # and then create pack operations for the top-level packages found
        for pack in top_lvl_packages:
            pack_quant_ids = pack_obj.get_content(cr, uid, [pack.id], context=context)
            pack_quants = quant_obj.browse(cr, uid, pack_quant_ids, context=context)
            vals.append({
                    'picking_id': picking.id,
                    'package_id': pack.id,
                    'product_qty': 1.0,
                    'location_id': pack.location_id.id,
                    'location_dest_id': quants_suggested_locations[pack_quants[0]],
                    'owner_id': pack.owner_id.id,
                })
            #remove the quants inside the package so that they are excluded from the rest of the computation
            for quant in pack_quants:
                del quants_suggested_locations[quant]

        # Go through all remaining reserved quants and group by product, package, lot, owner, source location and dest location
        for quant, dest_location_id in quants_suggested_locations.items():
#             key = (quant.product_id.id, quant.package_id.id, quant.lot_id.id, quant.owner_id.id, quant.location_id.id, dest_location_id, quant.reservation_id.lot_id.id)
            key = (quant.product_id.id, quant.package_id.id, quant.lot_id.id,
                   quant.owner_id.id, quant.location_id.id, dest_location_id,
#                    quant.reservation_id.lot_id.id,
                   quant.reservation_id.procurement_id.sale_line_id.id)  # yoshi
            if qtys_grouped.get(key):
                qtys_grouped[key] += quant.qty
            else:
                qtys_grouped[key] = quant.qty
     
        # Do the same for the forced quantities (in cases of force_assign or incoming shipment for example)
        for product, qty in forced_qties.items():
            if qty <= 0:
                continue
            suggested_location_id = _picking_putaway_apply(product)
#             key = (product.id, False, False, picking.owner_id.id, picking.location_id.id, suggested_location_id)
            key = (product.id, False, False, picking.owner_id.id, picking.location_id.id, suggested_location_id, False)  # yoshi
            if qtys_grouped.get(key):
                qtys_grouped[key] += qty
            else:
                qtys_grouped[key] = qty

        # Create the necessary operations for the grouped quants and remaining qtys
        uom_obj = self.pool.get('product.uom')
        prevals = {}
        for key, qty in qtys_grouped.items():
            product = self.pool.get("product.product").browse(cr, uid, key[0], context=context)
            uom_id = product.uom_id.id
            qty_uom = qty #oscg
            if product_uom.get(key[0]): #oscg
                uom_id = product_uom[key[0]].id #oscg
                qty_uom = uom_obj._compute_qty(cr, uid, product.uom_id.id, qty, uom_id) #oscg
            if product.product_tmpl_id.categ_id.enforce_qty_1:
                first_time = False
                for i in range(int(qty)):#oscg
                    val_dict = { #oscg
                        'picking_id': picking.id, #oscg
                        'product_qty': 1.0, #oscg
                        'product_id': key[0], #oscg
                        'package_id': key[1] if not first_time else False, #oscg
                        'lot_id': key[2] if not first_time else False, #oscg
                        'owner_id': key[3], #oscg
                        'location_id': key[4], #oscg
                        'location_dest_id': key[5], #oscg
                        'sale_line_id': key[6], #oscg yoshi
                        'product_uom_id': uom_id, #oscg
                    }
                    if key[0] in prevals: #oscg
                        prevals[key[0]].append(val_dict) #oscg
                    else:  #oscg
                        prevals[key[0]] = [val_dict] #oscg
                    first_time = True #oscg
            else:
                val_dict = {
                    'picking_id': picking.id,
                    'product_qty': qty_uom,
                    'product_id': key[0],
                    'package_id': key[1],
                    'lot_id': key[2],
                    'owner_id': key[3],
                    'location_id': key[4],
                    'location_dest_id': key[5],
                    'sale_line_id': key[6], #oscg yoshi
                    'product_uom_id': uom_id,
                }
                if key[0] in prevals:
                    prevals[key[0]].append(val_dict)
                else:
                    prevals[key[0]] = [val_dict]
                    
        # prevals var holds the operations in order to create them in the same order than the picking stock moves if possible
        processed_products = set()

        ''' >>> heavily changed from standard logic (OSCG) '''
        product_counter = {}
        product_counter_max = {}
        for pre in prevals:  # `pre` is a product id
            product_counter_max[pre] = len(prevals[pre])
            product_counter[pre] = 0

        for move in [x for x in picking.move_lines if x.state not in ('done', 'cancel')]:
            if move.product_id.id in prevals and move.product_id.id not in processed_products:
                if product_counter[move.product_id.id] >= product_counter_max[move.product_id.id]:
                    continue
                new_value = prevals.get(move.product_id.id, [])
                if new_value and move.product_id.product_tmpl_id.categ_id.enforce_qty_1: # Checking year since move lines can have same products and enforced.
                    # If purchase order line has serial number (MTO case) and when we create incoming shipment from PO
                    # then that serial number should be passed to the respective transfer (pack operation) on incoming
                    # shipments.
                    if move.procurement_id.purchase_line_id and move.procurement_id.purchase_line_id.lot_id \
                            and not new_value[product_counter[move.product_id.id]].get('lot_id', False):
                        if move.product_id.product_tmpl_id.categ_id.enforce_qty_1 \
                                and self.check_mto(cr, uid, move.procurement_id, context=context):
                            new_value[product_counter[move.product_id.id]].update({'lot_id': move.procurement_id.purchase_line_id.lot_id.id})
                    
                    # Below two conditions logic will pass the serial number on PO Line and SO Line if it was not given or left empty on time of Sales order creation.
                    if move.procurement_id.purchase_line_id and not move.procurement_id.purchase_line_id.lot_id:
                        if move.product_id.product_tmpl_id.categ_id.enforce_qty_1 and self.check_mto(cr, uid, move.procurement_id, context=context):
    #                     When receipt is done with serial number, it should trigger updating PO line, SO 
    #                     line and delivery with the received serial number (in case serial number had 
    #                     been left blank in SO for ‘Make To Order’ case) 
                            new_value[product_counter[move.product_id.id]].update({'purchase_line_id': move.procurement_id.purchase_line_id.id})
                            if not move.procurement_id.move_dest_id.lot_id:
                                new_value[product_counter[move.product_id.id]].update({'move_dest_id': move.procurement_id.move_dest_id.id})
                    if move.procurement_id.sale_line_id and not move.procurement_id.sale_line_id.lot_id:
                        if move.product_id.product_tmpl_id.categ_id.enforce_qty_1 and self.check_mto(cr, uid, move.procurement_id, context=context):
    #                     When receipt is done with serial number, it should trigger updating PO line, SO 
    #                     line and delivery with the received serial number (in case serial number had 
    #                     been left blank in SO for ‘Make To Order’ case) 
                            new_value[product_counter[move.product_id.id]].update({'sale_line_id': move.procurement_id.sale_line_id.id})
                    vals += [new_value[product_counter[move.product_id.id]]]
                    product_counter[move.product_id.id] += 1
                else:
                    vals += new_value # prevals.get(move.product_id.id, [])
                    processed_products.add(move.product_id.id)
            ''' <<< heavily changed from standard logic (OSCG) '''
        return vals

    def check_mto(self, cr, uid, procurement, context=None):
        # Method to check if procurement is MTO kind or not.
        if context is None:
            context = {}
        model, res_id1 = self.pool['ir.model.data'].get_object_reference(cr, uid, 'stock', 'route_warehouse0_mto')
        mto = False
        for route in procurement.route_ids:
            if route.id == res_id1:
                mto = True
        if mto:
            return True
        return False

    def action_confirm(self, cr, uid, ids, context=None):
        context = context or {}
        for pick in self.browse(cr, uid, ids, context=context):
            for m in pick.move_lines:
                if m.product_id.product_tmpl_id.categ_id.enforce_qty_1 \
                    and m.product_uom_qty > 1.0:
                    for qty in range(0, int(m.product_uom_qty - 1)):
                        default = {'product_uom_qty': 1.0,
                                   'product_uos_qty': 1.0}
                        move_line = self.pool.get('stock.move').copy(cr, uid,
                            m.id, default=default, context=context)
                    self.pool.get('stock.move').write(cr, uid, [m.id],
                        {'product_uom_qty': 1.0, 'product_uos_qty': 1.0},
                        context=context)
        return super(stock_picking, self).action_confirm(cr, uid, ids,
            context=context)

#     def action_button_split_line(self, cr, uid, ids, context=None):
#         context = context or {}
#         for pick in self.browse(cr, uid, ids, context=context):
#             if not pick.move_lines:
#                 raise osv.except_osv(_('Error!'),_('You cannot split a picking which has no move line.'))
#             for m in pick.move_lines:
#                 if m.product_id.product_tmpl_id.categ_id.enforce_qty_1 and m.product_uom_qty > 1.0:
#                     for qty in range(0, int(m.product_uom_qty - 1)):
#                         default = {'product_uom_qty': 1.0, 'product_uos_qty': 1.0}
#                         move_line = self.pool.get('stock.move').copy(cr, uid, m.id, default=default, context=context)
#                     self.pool.get('stock.move').write(cr, uid, [m.id], {'product_uom_qty': 1.0, 'product_uos_qty': 1.0}, context=context)
#             self.write(cr, uid, [pick.id], {'need_auto_split': False}, context=context)
#         return True

#     def _need_auto_split(self, cr, uid, ids, name, arg, context=None):
#         res = {}
#         for pick in self.browse(cr, uid, ids, context=context):
#             res[pick.id] = False
#             for m in pick.move_lines:
#                 if m.product_id.product_tmpl_id.categ_id.enforce_qty_1 and m.product_uom_qty > 1.0:
#                     res[pick.id] = True
#         return res
# 
#     _columns = {
#         'need_auto_split': fields.function(_need_auto_split, string='Need Auto Split?', 
#             type='boolean',
#             store={
#                 'stock.picking': (lambda self, cr, uid, ids, c={}: ids, [], 10),
#                 },
#             ),    
#     }
#     _defaults = {
#         'need_auto_split': True,
#     }
