# -*- coding: utf-8 -*-
# Copyright 2017-2018 Quartile Limited
# Copyright 2017 eHanse
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import openerp
from openerp.osv import fields, osv


class AccountVoucher(osv.osv):
    _inherit = 'account.voucher'
    # Also to be used as server action
    def update_invoice_lines(self, cr, uid, vals, ids, context=None):
        if 'move_line_id' in vals and 'reference' in vals:
            invoice_lines_object = self.pool.get('account.invoice.line')
            invoice_lines = invoice_lines_object.search(cr, uid,
                                                        [('invoice_id', '=', vals['move_line_id'])], context=context
                                                        )
            if invoice_lines:
                for lines in invoice_lines:
                    lines.payment_ref = vals['reference']

    def create(self, cr, uid, vals, context=None):
        res = super(AccountVoucher, self).create(cr, uid, vals, context=context)
        self.update_invoice_lines(self, cr, uid, vals, context=None)

        return res


    #     def get_vouchers_sale_order(self, cr, uid, ids, context=None):
    #     voucher_lines = self.pool.get('account.voucher.line')
    #     for this in self.browse(cr, uid, ids, context=context):
    #         voucher_lines_ids = voucher_lines.search(cr, uid,
    #                                                  [('voucher_id', '=', this.id),
    #                                                   ('vouchers_lines_ref', 'like', 'SO%')
    #                                                   ], context=context
    #
    #                                                  )
    #         if voucher_lines_ids:
    #             voucher_line_id = voucher_lines.browse(cr, uid, voucher_lines_ids, context=context)[0]
    #             this.vouchers_sales_order = voucher_line_id.vouchers_lines_ref
    #
    # def create(self, cr, uid, vals, context=None):
    #     res = super(account_voucher_ext, self).create(cr, uid, vals, context=context)
    #     self.get_vouchers_sale_order(cr, uid, [res], context=context)
    #     return res




    #
    # def create(self, vals):
    #     if 'move_line_id' in vals and 'reference' in vals:
    #         # Check relateed invoice lines
    #         invoice_lines_object = self.env['account.invoice.lines']
    #         domain = [
    #             ('invoice_id', '=', vals['move_line_id']),
    #         ]
    #         invoice_lines = invoice_lines_object.search(domain)
    #         if invoice_lines:
    #
    #             for lines in invoice_lines:
    #                 lines.payment_ref = vals['reference']
    #     res = super(AccountVoucher, self).create(vals)
    #     return res
