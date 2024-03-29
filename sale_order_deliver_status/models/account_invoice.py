# Copyright 2019 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    # Adds triggering points to account invoice operations for re-computing
    # order_status.
    @api.multi
    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)
        if "state" in vals:
            self.mapped("invoice_line_ids").mapped("sale_line_ids").mapped(
                "order_id"
            )._compute_order_status()
        return res
