# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ProductCondition(models.Model):
    _name = "product.condition"

    name = fields.Char("Name", required=True, translate=True)
    description = fields.Char("Description", required=True, translate=True)

    @api.multi
    def name_get(self):
        res = []
        for condition in self:
            res.append(
                (condition.id, "{}: {}".format(condition.name, condition.description))
            )
        return res
