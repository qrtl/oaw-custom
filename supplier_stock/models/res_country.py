# -*- coding: utf-8 -*-
# Copyright 2017 Rooms For (Hong Kong) Limted T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _


class ResCountry(models.Model):
    _inherit = "res.country"

    supplier_stock = fields.Boolean(
        string='Keeps Supplier Stock',
        help='Select if this country is used for "Supplier Stock" records.'
    )
    supplier_lead_time = fields.Integer(
        string='Supplier Lead Time (Days)',
    )
