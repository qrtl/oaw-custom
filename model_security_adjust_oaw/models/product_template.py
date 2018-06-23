# -*- coding: utf-8 -*-
# Copyright 2017 Rooms For (Hong Kong) Limted T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


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
        description = self.name
        if "AC" in description:
            self.material = "QZ"
        elif "5N" in description:
            self.material = "Rose Gold"
        elif "OG" in description:
            self.material = "White Gold"
        else:
            self.material = "Steel"
        if "QZ" in description:
            self.movement = "Quartz"
        else:
            self.movement = "Automatic"

