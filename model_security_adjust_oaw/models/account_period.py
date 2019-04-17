# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class AccountPeriod(models.Model):
    _inherit = 'account.period'

    allow_supplier_access = fields.Boolean(
        'Allow Supplier Access',
        related='fiscalyear_id.allow_supplier_access',
        readonly=True,
    )
