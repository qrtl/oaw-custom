# Copyright 2020 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockDataPurchaseHistory(models.Model):
    _name = "stock.data.purchase.history"

    supplier_id = fields.Many2one("res.partner", string="Supplier",)
    product_category_ids = fields.Many2many(
        "product.category", string="Purchased Brands",
    )
    sale_order_id = fields.Many2one("sale.order", string="Sales Order",)
    purchase_date = fields.Datetime(string="Purchased Date",)
    payment_confirm = fields.Boolean(string="Payment Confirm",)

    @api.multi
    def generate_purchased_stock_data(self):
        self.ensure_one()
        if not self.payment_confirm:
            raise UserError(_("You can only generate stock data from paid history"))
        # Remove all old records
        self.env["supplier.stock"].search(
            [
                ("prod_cat_selection", "in", self.product_category_ids.ids),
                ("readonly_record", "=", True),
                ("partner_id", "=", self.supplier_id.id),
            ]
        ).unlink()

        # Generate purchased stock data
        products = (
            self.env["product.product"]
            .sudo()
            .search(
                [
                    ("categ_id", "in", self.product_category_ids.ids),
                    ("type", "=", "product"),
                ]
            )
        )
        stock_data_supplier_location_id = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "supplier_user_stock_data_purchase.stock_data_supplier_location_id"
            )
        )
        for product in products:
            supplier_stock_vals = {
                "readonly_record": True,
                "partner_id": self.supplier_id.id,
                "product_id": product.id,
                "prod_cat_selection": product.categ_id.id,
                "partner_loc_id": int(stock_data_supplier_location_id),
                "quantity": 0,
                "currency_id": self.env.user.company_id.currency_id.id,
                "retail_in_currency": product.list_price,
                "price_unit": product.list_price,
            }
            self.env["supplier.stock"].sudo().create(supplier_stock_vals)