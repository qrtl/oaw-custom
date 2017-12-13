# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    currency_id_name = fields.Char(
        related='currency_id.name',
        readonly=True,
        store=True,
        require=True,
    )
