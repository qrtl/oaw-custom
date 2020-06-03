# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductPartsStatus(models.Model):
    _name = "product.parts.status"

    name = fields.Char("Name", required=True, translate=True)
