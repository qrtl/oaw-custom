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
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools import  DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _


class stock_quant(osv.osv):
    _inherit = "stock.quant"
    
    def _actual_qty(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for quant in self.browse(cr, uid, ids, context=context):
            res[quant.id] = quant.qty - quant.sale_reserver_qty
        return res
    
    _description = "Stock Quants"
    _columns = {
        'usage': fields.related('location_id', 'usage', type='char', string='Type of Location', readonly=True, store=True),
        'sale_reserver_qty': fields.float('Sale Reserved Quantity'),#Added this field to track if selected quant on other sale order should not be select again.
        'actual_qty': fields.function(_actual_qty, string='Actual Quantity', help="It is: Quantity - Sale Reserved Quantity", type='float', store={
                'stock.quant': (lambda self, cr, uid, ids, c={}: ids, [], 10),
            },),
    }
    
class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'is_enforce_qty': fields.boolean('Is Enforce Quantity 1?', help="This field will be ticked if one of sales order line has product which enforce quantity from its category."),
        'lot_id': fields.related('order_line', 'lot_id', type='many2one', relation='stock.production.lot', string='Lot'), #For search purpose
        'order_policy': fields.selection([
                ('manual', 'On Demand'),
                ('picking', 'On Delivery Order'),
                ('prepaid', 'Before Delivery Order'),
                ('delivery', 'On Delivery (per SO Line)'),# Added this new option.
            ], 'Create Invoice', required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
            help="""This field controls how invoice and delivery operations are synchronized."""),
    }
    
    def action_wait(self, cr, uid, ids, context=None):
#        Add a new option 'On Delivery (per SO Line)' for 'Create Invoice' field in 
#        SO.  In case this option is selected, user should be able to create an 
#        invoice any time from SO.  However, user should not be able to process 
#        'Transfer' in outgoing delivery for lines (stock moves) for which payment 
#        has yet to be done. 
#This complete override the action_wait method.
        
        context = context or {}
        for o in self.browse(cr, uid, ids):
            if not o.order_line:
                raise osv.except_osv(_('Error!'),_('You cannot confirm a sales order which has no line.'))
            noprod = self.test_no_product(cr, uid, o, context)
            if (o.order_policy in ('delivery', 'manual')) or noprod: #Added one more option delivery here.
                self.write(cr, uid, [o.id], {'state': 'manual', 'date_confirm': fields.date.context_today(self, cr, uid, context=context)})
            else:
                self.write(cr, uid, [o.id], {'state': 'progress', 'date_confirm': fields.date.context_today(self, cr, uid, context=context)})
            self.pool.get('sale.order.line').button_confirm(cr, uid, [x.id for x in o.order_line])
        return True
    
    def onchange_partner_id(self, cr, uid, ids, part, context=None):
#        Add logic to propose Create Invoice (order_policy) in SO from customer 
#(add a field in customer) 
        res = super(sale_order, self).onchange_partner_id(cr, uid, ids, part, context=context)
        if not part:
            return res
        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
        res['value'].update({'order_policy': part.order_policy})
        return res
    
    def _prepare_order_line_procurement(self, cr, uid, order, line, group_id=False, context=None):
        #Send/Pass lot, quant and enforce_qty_1 to the respected procurement using sale order lines. This will be used in pickings/moves.
        """ create procurement here we add just two fields add quant_id and lot_id"""
        res = super(sale_order,self)._prepare_order_line_procurement(cr, uid, order, line, group_id, context=context)
        res.update({'quant_id': line.quant_id.id, 'lot_id':line.lot_id.id, 'is_enforce_qty': line.product_id.product_tmpl_id.categ_id.enforce_qty_1})
        return res 
    
    def action_ship_create(self, cr, uid, ids, context=None):
        res = super(sale_order, self).action_ship_create(cr, uid, ids, context=context)
        for order in self.browse(cr, uid, ids, context=context):
            for line in order.order_line:
                if line.product_id.product_tmpl_id.categ_id.enforce_qty_1:# Just flag SO as enforce qty SO.
                    order.write({'is_enforce_qty': True})
                if line.quant_id and line.lot_id:
#                    For serial number availability in SO line, selection should be limited to the ones 
#that (1) have on­hand qty > 0, and (2) are not reserved by another SO. 
                    current_qty = line.quant_id.sale_reserver_qty + line.product_uom_qty
                    line.quant_id.write({'sale_reserver_qty': current_qty})
        return res
    

class procurement_order(osv.osv):
    _inherit = "procurement.order"
    _columns = {
        'quant_id': fields.many2one('stock.quant', string="Quant From Sale Line"),
        'lot_id': fields.many2one('stock.production.lot', string="Stock Production lot From Sale Line", help="From Sales Order Line"),
        'is_enforce_qty': fields.boolean('Is Enforce Quantity 1?')
    }
    
    def _run_move_create(self, cr, uid, procurement, context=None):
        """ move are create based on procurment """
        res = super(procurement_order,self)._run_move_create(cr, uid, procurement, context)
        res.update({'quant_id': procurement.quant_id.id, 'lot_id': procurement.lot_id.id}) #Add lot and quant ref on related stock move of procurement order.
        return res
    
    def check_both_vci_mto(self, cr, uid, procurement, context=None):
        #TODO: Can be remove since not used anywhere.
        if context is None:
            context = {}
        model, res_id1 = self.pool['ir.model.data'].get_object_reference(cr, uid, 'stock', 'route_warehouse0_mto')
        model, res_id2 = self.pool['ir.model.data'].get_object_reference(cr, uid, 'vendor_consignment_stock', 'route_warehouse0_buy_vci')
        vci = False
        mto = False
        for route in procurement.route_ids:
            if route.id == res_id1:
                mto = True
            if route.id == res_id2:
                vci = True
        if vci and mto:
            return True
        return False
    
    def check_vci_or_mto(self, cr, uid, procurement, context=None):
        #This method will check if the given procurement is set with MTO and VCI or not.
#       It will be used in logic of "Prevent multiple procurements getting merged into one PO.  SO and PO 
#should be one to one relationship for ‘Make To Order’ and ‘Buy VCI’ cases."

        if context is None:
            context = {}
        model, res_id1 = self.pool['ir.model.data'].get_object_reference(cr, uid, 'stock', 'route_warehouse0_mto')
        model, res_id2 = self.pool['ir.model.data'].get_object_reference(cr, uid, 'vendor_consignment_stock', 'route_warehouse0_buy_vci')
        vci = False
        mto = False
        for route in procurement.route_ids:
            if route.id == res_id1:
                mto = True
            if route.id == res_id2:
                vci = True
        if vci or mto:
            return True
        return False
    
    def _get_po_line_values_from_proc(self, cr, uid, procurement, partner, company, schedule_date, context=None):
        res = super(procurement_order, self)._get_po_line_values_from_proc(cr, uid, procurement, partner, company, schedule_date, context=context)
        if self.check_vci_or_mto(cr, uid, procurement, context=context):
            # Pass the lot_id reference on PO Line from procurement object.
            res.update({'lot_id': procurement.lot_id.id})
        return res
    
    def make_po(self, cr, uid, ids, context=None):
        """ Resolve the purchase from procurement, which may result in a new PO creation, a new PO line creation or a quantity change on existing PO line.
        Note that some operations (as the PO creation) are made as SUPERUSER because the current user may not have rights to do it (mto product launched by a sale for example)

        @return: dictionary giving for each procurement its related resolving PO line.
        """
        res = {}
        company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
        po_obj = self.pool.get('purchase.order')
        po_line_obj = self.pool.get('purchase.order.line')
        seq_obj = self.pool.get('ir.sequence')
        pass_ids = []
        linked_po_ids = []
        sum_po_line_ids = []
        for procurement in self.browse(cr, uid, ids, context=context):
            partner = self._get_product_supplier(cr, uid, procurement, context=context)
            if not partner:
                self.message_post(cr, uid, [procurement.id], _('There is no supplier associated to product %s') % (procurement.product_id.name))
                res[procurement.id] = False
            else:
                schedule_date = self._get_purchase_schedule_date(cr, uid, procurement, company, context=context)
                purchase_date = self._get_purchase_order_date(cr, uid, procurement, company, schedule_date, context=context) 
                line_vals = self._get_po_line_values_from_proc(cr, uid, procurement, partner, company, schedule_date, context=context)
                #look for any other draft PO for the same supplier, to attach the new line on instead of creating a new draft one
                available_draft_po_ids = po_obj.search(cr, uid, [
                    ('partner_id', '=', partner.id), ('state', '=', 'draft'), ('picking_type_id', '=', procurement.rule_id.picking_type_id.id),
                    ('location_id', '=', procurement.location_id.id), ('company_id', '=', procurement.company_id.id), ('dest_address_id', '=', procurement.partner_dest_id.id)], context=context)

                #"Prevent multiple procurements getting merged into one PO.  SO and PO 
#should be one to one relationship for ‘Make To Order’ and ‘Buy VCI’ cases."
                if available_draft_po_ids and not self.check_vci_or_mto(cr, uid, procurement, context=context):#probuse # Do we need to check if product is enforce qty or not ?
                    po_id = available_draft_po_ids[0]
                    po_rec = po_obj.browse(cr, uid, po_id, context=context)
                    #if the product has to be ordered earlier those in the existing PO, we replace the purchase date on the order to avoid ordering it too late
                    if datetime.strptime(po_rec.date_order, DEFAULT_SERVER_DATETIME_FORMAT) > purchase_date:
                        po_obj.write(cr, uid, [po_id], {'date_order': purchase_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}, context=context)
                    #look for any other PO line in the selected PO with same product and UoM to sum quantities instead of creating a new po line
                    available_po_line_ids = po_line_obj.search(cr, uid, [('order_id', '=', po_id), ('product_id', '=', line_vals['product_id']), ('product_uom', '=', line_vals['product_uom'])], context=context)
                    if available_po_line_ids:
                        po_line = po_line_obj.browse(cr, uid, available_po_line_ids[0], context=context)
                        po_line_obj.write(cr, SUPERUSER_ID, po_line.id, {'product_qty': po_line.product_qty + line_vals['product_qty']}, context=context)
                        po_line_id = po_line.id
                        sum_po_line_ids.append(procurement.id)
                    else:
                        line_vals.update(order_id=po_id)
                        po_line_id = po_line_obj.create(cr, SUPERUSER_ID, line_vals, context=context)
                        linked_po_ids.append(procurement.id)
                else:
                    name = seq_obj.get(cr, uid, 'purchase.order') or _('PO: %s') % procurement.name
                    po_vals = {
                        'name': name,
                        'origin': procurement.origin,
                        'partner_id': partner.id,
                        'location_id': procurement.location_id.id,
                        'picking_type_id': procurement.rule_id.picking_type_id.id,
                        'pricelist_id': partner.property_product_pricelist_purchase.id,
                        'currency_id': partner.property_product_pricelist_purchase and partner.property_product_pricelist_purchase.currency_id.id or procurement.company_id.currency_id.id,
                        'date_order': purchase_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'company_id': procurement.company_id.id,
                        'fiscal_position': partner.property_account_position and partner.property_account_position.id or False,
                        'payment_term_id': partner.property_supplier_payment_term.id or False,
                        'dest_address_id': procurement.partner_dest_id.id,
                    }
                    po_id = self.create_procurement_purchase_order(cr, SUPERUSER_ID, procurement, po_vals, line_vals, context=context)
                    po_line_id = po_obj.browse(cr, uid, po_id, context=context).order_line[0].id
                    pass_ids.append(procurement.id)
                res[procurement.id] = po_line_id
                self.write(cr, uid, [procurement.id], {'purchase_line_id': po_line_id}, context=context)
        if pass_ids:
            self.message_post(cr, uid, pass_ids, body=_("Draft Purchase Order created"), context=context)
        if linked_po_ids:
            self.message_post(cr, uid, linked_po_ids, body=_("Purchase line created and linked to an existing Purchase Order"), context=context)
        if sum_po_line_ids:
            self.message_post(cr, uid, sum_po_line_ids, body=_("Quantity added in existing Purchase Order Line"), context=context)
        return res


class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
#     _description = " "

    _columns = {
        'quant_id': fields.many2one('stock.quant', string="Stock Quant",),
        'lot_id': fields.many2one('stock.production.lot', string="Case No.",),
        'mto': fields.boolean('Is MTO?'),
    }
    
    def onchange_route(self, cr, uid, ids, route_id, context=None):
        # Serial number can be left blank in case of ‘Make To Order’. 
        # Otherwise, the field should be mandatory 
        result = {'mto': False}
        model, res_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'stock', 'route_warehouse0_mto')
        if route_id == res_id:
            result = {
                'mto': True,
            }
        return {'value': result}

    def onchange_quant(self, cr, uid, ids, quant_id, context=None):
        """ On change of quant_id finds lot_id(serial no)
        @param quant_id: Quant id
        @return: Dictionary of values
        """
#        Selecting a serial number (a quant) in SO should automatically propose 
#the Stock Owner in SO line 
#        Cost Price in SO line (we select ‘Display margins on sales orders’ in sales 
#configuration) should be taken from selected quant (serial number) 

        result = {}
        if quant_id:
            quant = self.pool.get('stock.quant').browse(cr,uid,quant_id)
            model, res_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'base', 'main_partner')
            result = {
                'lot_id': quant.lot_id.id,
                'stock_owner_id': quant.owner_id.id if not quant.owner_id.id == res_id else False, #Selecting a serial number (a quant) in SO should automatically propose the Stock Owner in SO line
                'purchase_price': quant.inventory_value / quant.qty
            }
        return {'value': result}
    
    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        res = super(sale_order_line, self)._prepare_order_line_invoice_line(cr, uid, line, account_id=account_id, context=context)
        # Pass the lot reference to invoice from SO / PO.
        res.update({'lot_id': line.lot_id.id})
        return res


class stock_move(osv.osv):
    _inherit = 'stock.move'
    _columns = {
        'quant_id': fields.many2one('stock.quant',string="Stock Quant From Sale"),
        'lot_id': fields.many2one('stock.production.lot',string="Stock Production Lot From Sale"),
    }
    
    def _get_invoice_line_vals(self, cr, uid, move, partner, inv_type, context=None):
        res = super(stock_move, self)._get_invoice_line_vals(cr, uid, move, partner, inv_type, context=context)
        # Pass the lot reference if invoice created from pickings.
        res.update({'lot_id': move.lot_id.id})
        return res
    
    def action_assign(self, cr, uid, ids, context=None):
        """ Checks the product type and accordingly writes the state.
        """
        
        #NEED TO OVERRIDE COMPLETE METHOD SINCE LOGIC WAS INBETWEEN THE LINES. PLEASE CHECK TAG #probuse TAG FOR CHANGES DONE ON THIS.
        
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
                        
#                Add a serial number field in SO line, which should be passed to delivery order 
#to reserve a quant of the selected serial number                        
                        if record.move_id.quant_id:#probuse
                            quants = [(record.move_id.quant_id, record.move_id.quant_id.qty)]#probuse
                        else:#probuse
                            quants = quant_obj.quants_get_prefered_domain(cr, uid, ops.location_id, move.product_id, qty, domain=domain, prefered_domain_list=[], restrict_lot_id=move.restrict_lot_id.id, restrict_partner_id=move.restrict_partner_id.id, context=context)#probuse
                            
                        quant_obj.quants_reserve(cr, uid, quants, move, record, context=context)
        for move in todo_moves:
            if move.linked_move_operation_ids:
                continue
            #then if the move isn't totally assigned, try to find quants without any specific domain
            if move.state != 'assigned':
                qty_already_assigned = move.reserved_availability
                qty = move.product_qty - qty_already_assigned
                
#                Add a serial number field in SO line, which should be passed to delivery order 
#to reserve a quant of the selected serial number
                if move.quant_id:#probuse
                    quants = [(move.quant_id, qty)]#probuse
                else:#probuse
                    quants = quant_obj.quants_get_prefered_domain(cr, uid, move.location_id, move.product_id, qty, domain=main_domain[move.id], prefered_domain_list=[], restrict_lot_id=move.restrict_lot_id.id, restrict_partner_id=move.restrict_partner_id.id, context=context)#probuse
                
                a = self.pool.get('stock.move').read(cr,uid,move.id)
                quant_obj.quants_reserve(cr, uid, quants, move, context=context)

        #force assignation of consumable products and incoming from supplier/inventory/production
        if to_assign_moves:
            self.force_assign(cr, uid, to_assign_moves, context=context)
            
    def _prepare_procurement_from_move(self, cr, uid, move, context=None):
        res = super(stock_move, self)._prepare_procurement_from_move(cr, uid, move, context=context)
        # Pass the lot ref, to stock move.
        res.update({'lot_id': move.lot_id.id})
        return res
        

class product_category(osv.osv):
    _inherit = 'product.category'
    _columns = {
#        Add a boolean field ‘Enforce Qty 1’ in product category.  Apply following 
#        rules to products under this category 
#        i. Serial number + product should be unique in serial number master (stock.product.lot) 
#        ii.Qty on hand should not exceed 1 for serial number + product
#        iii. In all transactions where serial number appears, qty should always be 1 
#            1. Auto­split lines in transfer screen in the manner that qty 1 is 
#        enforced for each line 
        'enforce_qty_1': fields.boolean(string='ENFORCE QTY 1'),
    }


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
#        ii.Qty on hand should not exceed 1 for serial number + product
        for prod in self.browse(cr, uid, ids, context=context):
            if prod.product_id.product_tmpl_id.categ_id.enforce_qty_1:
                if prod.lot_balance > 1:
                    return False
        return True
        
    _constraints = [
        (_check_serial_enforce, 'Error ! Serial number must be unique per ENFORCE QTY 1 category product.', ['name', 'product_id']),
        (_check_serial_qty, 'Error ! Quantity on hand should not exceed 1 for product haveing ENFORCE QTY 1 set.', ['lot_balance'])
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
            key = (quant.product_id.id, quant.package_id.id, quant.lot_id.id, quant.owner_id.id, quant.location_id.id, dest_location_id, quant.reservation_id.lot_id.id)
            if qtys_grouped.get(key):
                qtys_grouped[key] += quant.qty
            else:
                qtys_grouped[key] = quant.qty
     
        # Do the same for the forced quantities (in cases of force_assign or incomming shipment for example)
        for product, qty in forced_qties.items():
            if qty <= 0:
                continue
            suggested_location_id = _picking_putaway_apply(product)
            key = (product.id, False, False, picking.owner_id.id, picking.location_id.id, suggested_location_id)
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
            qty_uom = qty # probuse
            if product_uom.get(key[0]): # probuse
                uom_id = product_uom[key[0]].id # probuse
                qty_uom = uom_obj._compute_qty(cr, uid, product.uom_id.id, qty, uom_id) # probuse
            if product.product_tmpl_id.categ_id.enforce_qty_1:
                first_time = False
                for i in range(int(qty)):# probuse
                    val_dict = { # probuse
                        'picking_id': picking.id, # probuse
                        'product_qty': 1.0, # probuse
                        'product_id': key[0], # probuse
                        'package_id': key[1] if not first_time else False, # probuse
                        'lot_id': key[2] if not first_time else False, # probuse
                        'owner_id': key[3], # probuse
                        'location_id': key[4], # probuse
                        'location_dest_id': key[5], # probuse
                        'product_uom_id': uom_id, # probuse
                    }
                    if key[0] in prevals: # probuse
                        prevals[key[0]].append(val_dict) # probuse
                    else:  # probuse
                        prevals[key[0]] = [val_dict] # probuse
                    first_time = True # probuse
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
                    'product_uom_id': uom_id,
                }
                if key[0] in prevals:
                    prevals[key[0]].append(val_dict)
                else:
                    prevals[key[0]] = [val_dict]
                    
        # prevals var holds the operations in order to create them in the same order than the picking stock moves if possible
        processed_products = set()
        for move in picking.move_lines:
            if move.product_id.id not in processed_products:
                new_value = prevals.get(move.product_id.id, [])
                
                
                
                if new_value and move.procurement_id.sale_line_id and move.procurement_id.sale_line_id.order_id.order_policy == 'delivery':
#                    m. Add a new option 'On Delivery (per SO Line)' for 'Create Invoice' field in 
#SO.  In case this option is selected, user should be able to create an 
#invoice any time from SO.  However, user should not be able to process 
#'Transfer' in outgoing delivery for lines (stock moves) for which payment 
#has yet to be done..
                    new_value[0].update({'invoice_state': move.procurement_id.sale_line_id.state}) # If payment not done then raise from transfer wizard on pickings.
                
                # If purchase order line has serial number (MTO case) and when we create incoming shipment from PO then that serial number should be pass to the respected transfer (pack operation) on incoming shipments.
                if new_value and move.procurement_id.purchase_line_id and move.procurement_id.purchase_line_id.lot_id and not new_value[0].get('lot_id', False):
                    if move.product_id.product_tmpl_id.categ_id.enforce_qty_1 and self.check_mto(cr, uid, move.procurement_id, context=context):
                        new_value[0].update({'lot_id': move.procurement_id.purchase_line_id.lot_id.id})
                
                
                # Below two conditions logic will pass the serial number on PO Line and SO Line if it was not given or left empty on time of Sales order creation.
                if new_value and move.procurement_id.purchase_line_id and not move.procurement_id.purchase_line_id.lot_id:
                    if move.product_id.product_tmpl_id.categ_id.enforce_qty_1 and self.check_mto(cr, uid, move.procurement_id, context=context):
#                     When receipt is done with serial number, it should trigger updating PO line, SO 
#                     line and delivery with the received serial number (in case serial number had 
#                     been left blank in SO for ‘Make To Order’ case) 
                        new_value[0].update({'purchase_line_id': move.procurement_id.purchase_line_id.id})
                        if not move.procurement_id.move_dest_id.lot_id:
                            new_value[0].update({'move_dest_id': move.procurement_id.move_dest_id.id})
                if new_value and move.procurement_id.sale_line_id and not move.procurement_id.sale_line_id.lot_id:
                    if move.product_id.product_tmpl_id.categ_id.enforce_qty_1 and self.check_mto(cr, uid, move.procurement_id, context=context):
#                     When receipt is done with serial number, it should trigger updating PO line, SO 
#                     line and delivery with the received serial number (in case serial number had 
#                     been left blank in SO for ‘Make To Order’ case) 
                        new_value[0].update({'sale_line_id': move.procurement_id.sale_line_id.id})
                        
                vals += new_value # prevals.get(move.product_id.id, [])
                processed_products.add(move.product_id.id)
        
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
    
class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        #new field on partner form.
        'order_policy': fields.selection([
                ('manual', 'On Demand'),
                ('picking', 'On Delivery Order'),
                ('prepaid', 'Before Delivery Order'),
                ('delivery', 'On Delivery (per SO Line)'),
            ], 'Create Invoice',
            help="""This field controls how invoice and delivery operations are synchronized on sales order."""),
    }
    
    _defaults = {
        'order_policy': 'manual',
    }


class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    _columns = {
        'lot_id': fields.many2one('stock.production.lot', string="Case No.",),
    }
    

class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    _columns ={
        'lot_id': fields.related('order_line', 'lot_id', type='many2one', relation='stock.production.lot', string='Lot'),# for searching purpose
    }
    
    def _check_invoice_type_vci(self, cr, uid, ids, context=None):# Constraint
        for prod in self.browse(cr, uid, ids, context=context):
            if prod.is_vci and prod.invoice_method == 'picking':
                return False
        return True
        
    _constraints = [
         (_check_invoice_type_vci, 'Error ! You can not create purchase order with option Vendor Consignment Inventory with invoice policy from incoming shipment.', ['is_vci'])
    ]
    
    def _choose_account_from_po_line_vic(self, cr, uid, po_line, context=None):
#        Adjustment on supplier invoice ­ in case of vendor consignment, the 
#system should propose Product COGS instead of GR/IR Clearing 

        fiscal_obj = self.pool.get('account.fiscal.position')
        property_obj = self.pool.get('ir.property')
        if po_line.product_id:
            acc_id = po_line.product_id.property_stock_account_output.id
            if not acc_id:
                acc_id = po_line.product_id.categ_id.property_stock_account_output_categ.id
            if not acc_id:
                raise osv.except_osv(_('Error!'), _('Define an stock output account for this product: "%s" (id:%d).') % (po_line.product_id.name, po_line.product_id.id,))
        else:
            acc_id = property_obj.get(cr, uid, 'property_stock_account_output_categ', 'product.category', context=context).id
        fpos = po_line.order_id.fiscal_position or False
        return fiscal_obj.map_account(cr, uid, fpos, acc_id)
    
    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        #GR/IR Clearing account (which is supposed to be an interim receipt account) should not appear in vendor consignment scenario since stock accounting is disabled in this case.  Below is the journal entries we expect for this scenario.
        # 
        #1. Receive consignment goods
        #-> No accounting entry (because owner = supplier)
        #2. Customer invoice
        #-> Dr) Accounts Receivable 120,000
        #    Cr) Sales 120,000
        #3. Delivery
        #-> No accounting entry (because owner = supplier)
        #4. Supplier invoice
        #-> Dr) Product COGS 100,000
        #    Cr) Accounts Payable 100,000
        #The main point here is the red part (Product COGS 100,000).  Following normal configuration, the system will propose GR/IR Clearing account (which we will set in property_account_expense of product or property_account_expense_categ of product category) in supplier invoice.  However, in case of invoice for vendor consignment, we want to post Cost of Goods Sold (which we will set in property_account_output of product or property_account_output_categ of product category).
        res = super(purchase_order, self)._prepare_inv_line(cr, uid, account_id, order_line, context=context)
        if order_line.order_id.is_vci:
            acc_id = self._choose_account_from_po_line_vic(cr, uid, order_line, context=context)
            res.update({'account_id': acc_id})
        res.update({'lot_id':order_line.lot_id.id})
        
        if not order_line.lot_id:
            if order_line.product_id.product_tmpl_id.categ_id.enforce_qty_1:
                res.update({'lot_id':order_line.procurement_ids[0].lot_id.id})
        
        return res


class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _columns ={
        'lot_id': fields.related('invoice_line', 'lot_id', type='many2one', relation='stock.production.lot', string='Lot'),#for search purpose
    }


class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'
    _columns = {
        'lot_id': fields.many2one('stock.production.lot', string="Case No."),
    }


class stock_pack_operation(osv.osv):
    _inherit = 'stock.pack.operation'
    _columns = {
        'invoice_state': fields.char('Invoice State'),
        'purchase_line_id': fields.many2one('purchase.order.line', 'PO Line ID'),
        'sale_line_id': fields.many2one('sale.order.line', 'SO Line ID'),
        'move_dest_id': fields.many2one('stock.move', 'Destination Move', help="Move which caused (created) the procurement"),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: