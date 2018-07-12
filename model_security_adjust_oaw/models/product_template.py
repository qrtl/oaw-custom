# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # Two fields computed when product_template is created
    # Computation to be executed for initialization with Server Action
    material = fields.Char(
        string="Material",
        compute="_get_material_and_movement",
    )
    movement = fields.Char(
        string="Movement",
        compute="_get_material_and_movement",
    )

    @api.multi
    def _get_material_and_movement(self):
        for pt in self:
            description = pt.name
            if "TT" in description:
                pt.material = "Titan"
            elif "5N" in description:
                pt.material = "Rose Gold"
            elif "CARBON" in description:
                pt.material = "CARBON"
            elif "OG" in description:
                pt.material = "White Gold"
            else:
                pt.material = "Steel"
            if "QZ" in description:
                pt.movement = "Quartz"
            else:
                pt.movement = "Automatic"
