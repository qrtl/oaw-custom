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

from openerp.osv import fields, osv
from openerp.tools.translate import _


class sale_order(osv.osv):
    _inherit = "sale.order"

    def action_button_split_line(self, cr, uid, ids, context=None):
        context = context or {}
        for sale in self.browse(cr, uid, ids, context=context):
            if not sale.order_line:
                raise osv.except_osv(_('Error!'),_('You cannot split a sales order which has no line.'))
            for line in sale.order_line:
                if line.product_id.product_tmpl_id.categ_id.enforce_qty_1 and line.product_uom_qty > 1.0:
                    for qty in range(0, int(line.product_uom_qty - 1)):
                        default = {'product_uom_qty': 1.0, 'product_uos_qty': 1.0}
                        sale_line_id = self.pool.get('sale.order.line').copy(cr, uid, line.id, default=default, context=context)
                    self.pool.get('sale.order.line').write(cr, uid, [line.id], {'product_uom_qty': 1.0, 'product_uos_qty': 1.0}, context=context)
                    self.write(cr, uid, [sale.id], {'is_enforce_qty': True}, context=context)
        return True

    def _need_auto_split(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for sale in self.browse(cr, uid, ids, context=context):
            res[sale.id] = False
            for line in sale.order_line:
                if line.product_id.product_tmpl_id.categ_id.enforce_qty_1 and line.product_uom_qty > 1.0:
                    res[sale.id] = True
        return res
    
    _columns = {
        'is_enforce_qty': fields.boolean('Enforce Quantity 1', help="This \
            field will be ticked if one of sales order line has product \
            which enforces quantity from its category."),
        'lot_id': fields.related('order_line', 'lot_id', type='many2one', relation='stock.production.lot', string='Lot'), #For search purpose
        'order_policy': fields.selection([
            ('manual', 'On Demand'),
            ('picking', 'On Delivery Order'),
            ('prepaid', 'Before Delivery Order'),
            ('line_check', 'Check per SO Line'),  # newly added
            ], 'Create Invoice', required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
            help="""This field controls how invoice and delivery operations are synchronized."""),
        'need_auto_split': fields.function(_need_auto_split, string='Need Auto Split?', 
            type='boolean', store={
            'sale.order': (lambda self, cr, uid, ids, c={}: ids, [], 10),
            },),    
    }
    
    def action_wait(self, cr, uid, ids, context=None):
    # Add a new option 'On Demand (per SO Line)' for 'Create Invoice' field in 
    # SO.  In case this option is selected, user should be able to create an 
    # invoice any time from SO.  However, user should not be able to process 
    # 'Transfer' in outgoing delivery for lines (stock moves) for which payment 
    # has yet to be done. 
    # This completely overrides the action_wait method.
        
        context = context or {}
        for o in self.browse(cr, uid, ids):
            if not o.order_line:
                raise osv.except_osv(_('Error!'),_('You cannot confirm a sales order which has no line.'))
            # check enforce qty 1
            for line in o.order_line:
                if line.product_id.product_tmpl_id.categ_id.enforce_qty_1 and line.product_uom_qty > 1.0:
                    raise osv.except_osv(_('Error!'),_('Quantity of SO line should be 1 (enforce quantity 1).'))
            noprod = self.test_no_product(cr, uid, o, context)
            if (o.order_policy in ('line_check', 'manual')) or noprod: #Added one more option delivery here.
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
#                 if line.quant_id and line.lot_id:
# #                    For serial number availability in SO line, selection should be limited to the ones 
# #that (1) have on­hand qty > 0, and (2) are not reserved by another SO. 
#                     current_qty = line.quant_id.sale_reserver_qty + line.product_uom_qty
#                     line.quant_id.write({'sale_reserver_qty': current_qty})
        return res

    def _check_lot_duplicate(self, cr, uid, ids, context=None):
        lot_ids = []
        for line in self.browse(cr, uid, ids, context).order_line:
            if line.lot_id:
                lot_ids.append(line.lot_id)
        if len(lot_ids) != len(set(lot_ids)):
            return False
        return True
        
    _constraints = [
         (_check_lot_duplicate, 'Error! You cannot select the same quant more than once in an SO.', ['order_line'])
    ]


class sale_order_line(osv.osv):
    _inherit = "sale.order.line"

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
