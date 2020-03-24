# Copyright 2020 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    category_name = fields.Char(string="Brand", related="categ_id.name", store=True)
    update_partner_stock = fields.Boolean(
        string="Update Purchase Partner Stock Records"
    )

    @api.multi
    def write(self, vals):
        if "list_price" in vals:
            vals["update_partner_stock"] = True
        return super(ProductTemplate, self).write(vals)
