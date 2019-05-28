# Copyright 2019 chrono123 & Quartile
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"

    additional_info = fields.Char(
        String= 'Additional Info'
    )