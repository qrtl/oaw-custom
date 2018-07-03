# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    material = fields.Char(
        string="Material",
        compute="_get_material_and_movement"
    )
    movement = fields.Char(
        string="Movement",
        compute="_get_material_and_movement"
    )

    @api.multi
    def _get_material_and_movement(self):
        for pt in self:
            description = pt.name
            if "AC" in description:
                pt.material = "QZ"
            elif "5N" in description:
                pt.material = "Rose Gold"
            elif "OG" in description:
                pt.material = "White Gold"
            else:
                pt.material = "Steel"
            if "QZ" in description:
                pt.movement = "Quartz"
            else:
                pt.movement = "Automatic"
