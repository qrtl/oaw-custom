# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class SupplierLocation(models.Model):
    _name = 'supplier.location'
    _description = 'Partner Location'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    supplier_lead_time = fields.Integer(
        string='Partner Lead Time (Days)',
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        help='Default currency to be proposed in Supplier Stock records.'
    )
    owner_id = fields.Many2one(
        string='Owner',
        comodel_name='res.partner',
    )

    _sql_constraints = [
        ('name_supp_location_uniq', 'unique(name)',
         'The name of the supplier location must be unique!'),
    ]
