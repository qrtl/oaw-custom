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
