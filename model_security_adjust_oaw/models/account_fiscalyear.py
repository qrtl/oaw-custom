# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class AccountFiscalyear(models.Model):
    _inherit = 'account.fiscalyear'

    allow_supplier_access = fields.Boolean(
        'Allow Supplier Access',
        default=False,
    )
