# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class AccountFiscalyear(models.Model):
    _inherit = 'account.fiscalyear'

    allow_supplier_access = fields.Boolean(
        'Allow Supplier Access',
        default=False,
    )
