# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    gender = fields.Selection([
        ("women", "Women's watch"),
        ("men_unisex", "Men's watch/Unisex")
    ], string="Gender", copy=False)
    movement = fields.Selection([
        ("automatic", "Automatic"),
        ("quartz", "Quartz"),
        ("manual", "Manual winding")
    ], string="Movement", copy=False)
    case_diameter_x = fields.Char("Case Diameter (mm)", copy=False)
    case_diameter_y = fields.Char("Case Diameter (mm)", copy=False)
    case_material = fields.Many2one(
        'product.material',
        domain="[('case_material', '=', True)]",
        string="Case Material",
        copy=False
    )
    bracelet_material = fields.Many2one(
        'product.material',
        domain="[('bracelet_material', '=', True)]",
        string="Bracelet Material", copy=False)
    clasp = fields.Selection([
        ("buckle", "Buckle"),
        ("fold_clasp", "Fold clasp"),
        ("jewelry_clasp", "Jewelry clasp")
    ], string="Clasp", copy=False)
    case_back = fields.Selection([
        ("solid", "Solid"),
        ("transparent", "Transparent")
    ], string="Case Back", copy=False)
