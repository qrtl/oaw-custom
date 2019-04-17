# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, osv
from odoo.tools.translate import _


class product_category(models.Model):
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

    
class res_partner(models.Model):
    _inherit = 'res.partner'
    _columns = {
        #new field on partner form.
        'order_policy': fields.selection([
                ('manual', 'On Demand'),
                ('picking', 'On Delivery Order'),
                ('prepaid', 'Before Delivery Order'),
#                 ('delivery', 'On Delivery (per SO Line)'),
                ('line_check', 'Check per SO Line'),
            ], 'Create Invoice',
            help="""This field controls how invoice and delivery operations are synchronized on sales order."""),
    }
    
    _defaults = {
        'order_policy': 'manual',
    }


class account_invoice(models.Model):
    _inherit = 'account.invoice'
    _columns ={
        'lot_id': fields.related('invoice_line', 'lot_id', type='many2one', relation='stock.production.lot', string='Lot'),#for search purpose
    }


class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'
    _columns = {
        'lot_id': fields.many2one('stock.production.lot', string="Case No."),
    }

class stock_pack_operation(models.Model):
    _inherit = 'stock.pack.operation'
    _columns = {
        'invoice_state': fields.char('Invoice State'),
        'purchase_line_id': fields.many2one('purchase.order.line', 'PO Line ID'),
        'sale_line_id': fields.many2one('sale.order.line', 'SO Line ID'),
        'move_dest_id': fields.many2one('stock.move', 'Destination Move', help="Move which caused (created) the procurement"),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: