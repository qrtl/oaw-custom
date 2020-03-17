# Copyright 2020  Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductsSalesInit(models.TransientModel):
    _name = "products.sales.wizard"
    _description = "Products Sales Initialization Wizard "

    product_ids = fields.Many2many("product.template", string="Products")

    @api.model
    def default_get(self, field_names):
        defaults = super().default_get(field_names)
        product_ids = self.env.context["active_ids"]
        defaults["product_ids"] = product_ids
        return defaults

    @api.multi
    def action_products_sales_initialise_btn(self):
        self.ensure_one()
        self.env["product.template"]._initialize_values(self.product_ids)
        return {"type": "ir.actions.act_window_close"}
