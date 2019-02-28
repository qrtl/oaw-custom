# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class SupplierLocation(models.Model):
    _inherit = "supplier.location"

    hk_location = fields.Boolean(
        string="HK Location",
        default=False,
    )
