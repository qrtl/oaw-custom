# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    gender = fields.Char("Gender")
    movement = fields.Char("Movement")
    case_diameter = fields.Float("Case Diameter (mm)")
    case_material = fields.Char("Case Material")
    bracelet_material = fields.Char("Bracelet Material")
    clasp = fields.Char("Clasp")
    case_back = fields.Char("Case Back")
