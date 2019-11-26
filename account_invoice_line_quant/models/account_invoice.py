# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    # For Search
    lot_id = fields.Many2one(related="invoice_line_ids.lot_id", string="Lot")
