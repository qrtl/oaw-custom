# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    payment_ref= fields.Char(
        string='Payment Reference',
        compute = '_get_payment_reference',
    )

    @api.multi
    @api.depends('payment_ids')
    def _get_payment_reference(self):
        for invoice in self:
            payment_ref = []
            for line in invoice.payment_ids:
                if line.ref not in payment_ref:
                    payment_ref.append(line.ref)
            invoice.payment_ref = ','.join(payment_ref) if len(
                payment_ref) > 0 else False
