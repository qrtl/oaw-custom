# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    paid_date = fields.Date(
        readonly=True,
        compute='get_paid_date_info',
        string='Paid Date'
    )
    paid_date_currency_rate = fields.Float(
        readonly=True,
        compute='get_paid_date_info',
        string='Paid Day Currency Rate'
    )

    @api.multi
    def get_paid_date_info(self):
        for account_invoice in self:
            if account_invoice.state == 'paid':
                paid_date = False
                for payment_id in account_invoice.payment_ids:
                    if not paid_date or\
                            (paid_date and payment_id.move_id.date > paid_date):
                        paid_date = payment_id.move_id.date
                if paid_date:
                    account_invoice.paid_date = paid_date
                    if account_invoice.currency_id == \
                            account_invoice.company_id.currency_id:
                        rate = 1.0
                    else:
                        rate = account_invoice.env[
                                   'res.currency.rate'].search([
                            ('currency_id', '=', account_invoice.currency_id.id),
                            ('name', '<=', paid_date),
                        ], order='name desc', limit=1).rate or 1.0
                    account_invoice.paid_date_currency_rate = rate
        return
