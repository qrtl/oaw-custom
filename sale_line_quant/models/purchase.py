# -*- coding: utf-8 -*-
# Copyright 2015-2017 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, osv
from openerp.tools.translate import _


class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    _columns = {
        'lot_id': fields.many2one('stock.production.lot', string="Case No.", copy=False),
        'mto': fields.boolean('Is MTO?', readonly=True, copy=False),
        'vci': fields.boolean('Is VCI?', readonly=True, copy=False),
    }


class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    _columns ={
        'lot_id': fields.related('order_line', 'lot_id', type='many2one',
                relation='stock.production.lot', string='Lot'),  # for search purpose
        'is_mto': fields.boolean('Make to Order', readonly=True, copy=False),
    }
    
    def _check_invoice_type_vci(self, cr, uid, ids, context=None):# Constraint
        for prod in self.browse(cr, uid, ids, context=context):
            if prod.is_vci and prod.invoice_method == 'picking':
                return False
        return True
        
    _constraints = [
         (_check_invoice_type_vci, 'Error! You cannot create purchase order with option Vendor Consignment Inventory with invoice policy from incoming shipment.', ['is_vci'])
    ]
    
    def _choose_account_from_po_line_vic(self, cr, uid, po_line, context=None):
        # Adjustment on supplier invoice ­ in case of vendor consignment, the
        # system should propose Product COGS instead of GR/IR Clearing
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
    
    # this method overrides the standard method
    def wkf_confirm_order(self, cr, uid, ids, context=None):
        todo = []
        for po in self.browse(cr, uid, ids, context=context):
            if not po.order_line:
                raise osv.except_osv(_('Error!'),_('You cannot confirm a purchase order without any purchase order line.'))
            for line in po.order_line:
                # >>> OSCG
                # check enforce qty 1
                if line.product_id.product_tmpl_id.categ_id.enforce_qty_1 and line.product_qty > 1.0:
                    raise osv.except_osv(_('Error!'),_('Quantity of PO line should be 1 (enforce quantity 1).'))
                # <<< OSCG
                if line.state=='draft':
                    todo.append(line.id)        
        self.pool.get('purchase.order.line').action_confirm(cr, uid, todo, context)
        for id in ids:
            self.write(cr, uid, [id], {'state' : 'confirmed', 'validator' : uid})
        return True
    
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
            if order_line.procurement_ids and order_line.product_id.product_tmpl_id.categ_id.enforce_qty_1:
                res.update({'lot_id':order_line.procurement_ids[0].lot_id.id})
        
        return res
