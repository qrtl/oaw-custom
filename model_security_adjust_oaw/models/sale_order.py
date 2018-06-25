# -*- coding: utf-8 -*-
from openerp import models, fields, osv
from openerp import workflow

class saleOrderSupplierAccess(models.Model):
    _inherit = 'sale.order'
    _description = 'Extends sale order: Print Button Supplier FM'

    def print_supplier_fm(self, cr, uid, ids, context=None):
        '''
        This function prints the the quotation  and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        self.signal_workflow(cr, uid, ids, 'quotation_sent')
        return self.pool['report'].get_action(cr, uid, ids, 'model_security_adjust_oaw.report_sale_supplier_fm', context=context)



from openerp.osv import osv, fields


class SaleOrder(osv.osv):
    _inherit = "sale.order"

    def action_supplier_view_delivery(self, cr, uid, ids, context=None):

        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(
            cr, uid, 'model_security_adjust_oaw', 'action_picking_tree_all')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]

        # compute the number of delivery orders to display
        pick_ids = []
        for so in self.browse(cr, uid, ids, context=context):
            pick_ids += [picking.id for picking in so.picking_ids]

        # choose the view_mode accordingly
        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(
                map(str, pick_ids)) + "])]"
        else:
            res = mod_obj.get_object_reference(
                cr, uid, 'model_security_adjust_oaw',
                'view_supplier_picking_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = pick_ids and pick_ids[0] or False

        return result
