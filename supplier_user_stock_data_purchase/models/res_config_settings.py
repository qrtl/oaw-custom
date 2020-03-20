# Copyright 2020 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    supplier_stock_data_product_id = fields.Many2one(
        "product.product", "Supplier Purchase Stock Data Product"
    )
    stock_data_supplier_location_id = fields.Many2one(
        "supplier.location", "Supplier Location for Stock Data"
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env["ir.config_parameter"].sudo().get_param
        res.update(
            supplier_stock_data_product_id=int(
                get_param(
                    "supplier_user_stock_data_purchase.supplier_stock_data_product_id",
                    default=False,
                )
            )
        )
        res.update(
            stock_data_supplier_location_id=int(
                get_param(
                    "supplier_user_stock_data_purchase.stock_data_supplier_location_id",
                    default=False,
                )
            )
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env["ir.config_parameter"].sudo().set_param
        set_param(
            "supplier_user_stock_data_purchase.supplier_stock_data_product_id",
            self.supplier_stock_data_product_id.id,
        )
        set_param(
            "supplier_user_stock_data_purchase.stock_data_supplier_location_id",
            self.stock_data_supplier_location_id.id,
        )
