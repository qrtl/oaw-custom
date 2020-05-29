# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductMaterial(models.Model):
    _name = "product.material"

    name = fields.Char(string="Name", translate=True)
    case_material = fields.Boolean("For Case")
    bracelet_material = fields.Boolean("For Bracelet")
