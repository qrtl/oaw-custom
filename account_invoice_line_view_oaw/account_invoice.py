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

from openerp import models, fields, api, _
from datetime import datetime
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
 

class InvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def _get_org_vals(self, inv_ln):
        so_id, po_id = 0, 0
        SO = self.env['sale.order']
        PO = self.env['purchase.order']
        if inv_ln.invoice_id.origin:
            if inv_ln.invoice_id.type == 'out_invoice' and \
                SO.search([('name','=',inv_ln.invoice_id.origin)]):
                so_id = \
                    SO.search([('name','=',inv_ln.invoice_id.origin)])[0].id
            if inv_ln.invoice_id.type == 'in_invoice' and \
                PO.search([('name','=',inv_ln.invoice_id.origin)]):
                po_id = \
                    PO.search([('name','=',inv_ln.invoice_id.origin)])[0].id
        return so_id, po_id
         
    @api.multi
    @api.depends('invoice_id.state','invoice_id.origin')
    def _get_vals(self):
        for inv_ln in self:
            inv_ln.so_id, inv_ln.po_id = self._get_org_vals(inv_ln)

    @api.multi
    def _get_base_amt(self):
        Invoice = self.env['account.invoice']
        Rate = self.env['res.currency.rate']
        for inv_ln in self:
            curr_amt = inv_ln.price_subtotal
            # set rate 1.0 if the transaction currency is the same as the base currency
            if inv_ln.currency_id == inv_ln.company_id.currency_id:
                rate = 1.0
            else:
                invoice_date = Invoice.browse([inv_ln.invoice_id.id])[0].date_invoice \
                    or inv_ln.env.context.get('date', datetime.today().strftime('%Y-%m-%d'))
                rate = Rate.search([
                    ('currency_id', '=', inv_ln.currency_id.id),
                    ('name', '<=', invoice_date),
                    ], order='name desc', limit=1).rate or 1.0
            inv_ln.rate = rate
            inv_ln.base_amt = curr_amt / rate


    user_id = fields.Many2one('res.users',
                              related='invoice_id.user_id',
                              store=True,
                              readonly=True,
                              string='Salesperson'
                              )
    number = fields.Char(related='invoice_id.number',
                         store=True,
                         readonly=True,
                         string='Number'
                         )
    state = fields.Selection(related='invoice_id.state',
                             store=True,
                             readonly=True,
                             string='Status'
                             )
    date_invoice = fields.Date(related='invoice_id.date_invoice',
                               store=True,
                               readonly=True,
                               string='Invoice Date'
                               )
    ref = fields.Char(related='invoice_id.partner_id.ref',
                      store=True,
                      readonly=True,
                      string='Partner Ref'
                      )
    period_id = fields.Many2one(related='invoice_id.period_id',
                                readonly=True,
                                string='Period'
                                )
    reference = fields.Char(related='invoice_id.reference',
                            readonly=True,
                            string='Invoice Ref'
                            )
    date_due = fields.Date(related='invoice_id.date_due',
                           readonly=True,
                           string='Due Date'
                           )
    currency_id = fields.Many2one(related='invoice_id.currency_id',
                                  readonly=True,
                                  string='Currency'
                                  )
    rate = fields.Float(compute='_get_base_amt',
                        readonly=True,
                        string='Rate'
                        )
    base_amt = fields.Float(compute='_get_base_amt',
                            digits_compute=dp.get_precision('Account'),
                            readonly=True,
                            string='Base Amount'
                            )
    so_id = fields.Many2one('sale.order',
                            compute='_get_vals',
                            store=True,
                            readonly=True,
                            string='SO'
                            )
    po_id = fields.Many2one('purchase.order',
                            compute='_get_vals',
                            store=True,
                            readonly=True,
                            string='PO'
                            )

 
    def init(self, cr):
        # to be executed only when installing the module.  update "stored" fields 
        sql = """
            update account_invoice_line l
            set state = inv.state,
                date_invoice = inv.date_invoice,
                ref = p.ref
            from account_invoice inv
            left join res_partner p on inv.partner_id = p.id
            where l.invoice_id = inv.id
            """
        cr.execute(sql)
