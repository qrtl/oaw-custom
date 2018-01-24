# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limted
# Copyright 2017 eHanse
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class SupplierLocation(models.Model):
    _name = "supplier.location"
    _description = "Partner Location"
    _order = "name"

    name = fields.Char(
        string="Name",
        required=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    supplier_lead_time = fields.Integer(
        string="Partner Lead Time (Days)",
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        help="Default currency to be proposed in Supplier Stock records."
    )

    _sql_constraints = [
        ('name_supp_location_uniq', 'unique(name)',
         'The name of the supplier location must be unique!'),
    ]
