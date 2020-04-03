# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models

local_supplier_location_param = (
    "supplier_user_stock_data_purchase.stock_data_local_supplier_location_id"
)
oversea_supplier_location_param = (
    "supplier_user_stock_data_purchase.stock_data_oversea_supplier_location_id"
)


class StockDataPurchaseHistory(models.Model):
    _name = "stock.data.purchase.history"

    supplier_id = fields.Many2one("res.partner", string="Supplier",)
    product_category_ids = fields.Many2many(
        "product.category", string="Purchased Brands",
    )
    sale_order_id = fields.Many2one("sale.order", string="Sales Order",)
    purchase_date = fields.Datetime(string="Purchased Date",)
    payment_confirm = fields.Boolean(string="Payment Confirm",)
    data_generation_pending = fields.Boolean(string="Data Generation Pending",)

    @api.multi
    def request_generate_stock_data(self):
        self.sudo().update({"data_generation_pending": True})

    @api.multi
    def generate_purchased_stock_data(self):
        for history in self:
            # Remove all old records
            self.env["supplier.stock"].search(
                [
                    ("prod_cat_selection", "in", history.product_category_ids.ids),
                    ("readonly_record", "=", True),
                    ("partner_id", "=", history.supplier_id.id),
                ]
            ).unlink()

            # Generate purchased stock data
            products = (
                self.env["product.product"]
                .sudo()
                .search(
                    [
                        ("categ_id", "in", history.product_category_ids.ids),
                        ("product_tmpl_id.qty_total", ">", 0),
                        ("type", "=", "product"),
                    ]
                )
            )
            stock_data_local_supplier_location_id = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(local_supplier_location_param)
            )
            stock_data_oversea_supplier_location_id = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(oversea_supplier_location_param)
            )
            for product in products:
                supplier_stock_vals = {
                    "readonly_record": True,
                    "partner_id": history.supplier_id.id,
                    "product_id": product.id,
                    "prod_cat_selection": product.categ_id.id,
                    "partner_loc_id": int(stock_data_local_supplier_location_id)
                    if product.product_tmpl_id.qty_local_stock
                    else int(stock_data_oversea_supplier_location_id),
                    "quantity": 0,
                    "website_quantity": str(int(product.product_tmpl_id.qty_total))
                    if product.product_tmpl_id.qty_total < 3
                    else "3",
                    "currency_id": self.env.user.company_id.currency_id.id,
                    "retail_in_currency": product.product_tmpl_id.net_price,
                    "price_unit": product.product_tmpl_id.net_price,
                }
                self.env["supplier.stock"].sudo().create(supplier_stock_vals)
            history.update({"data_generation_pending": False})

    def update_purchase_partner_stock_data(self):
        self.search(
            [("data_generation_pending", "=", True), ("payment_confirm", "=", True)]
        ).generate_purchased_stock_data()
        updated_products = self.env["product.template"].search(
            [("update_partner_stock", "=", True)]
        )
        stock_data_local_supplier_location_id = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(local_supplier_location_param)
        )
        stock_data_oversea_supplier_location_id = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(oversea_supplier_location_param)
        )
        for product in updated_products:
            supplier_stock_records = self.env["supplier.stock"].search(
                [
                    ("readonly_record", "=", True),
                    ("product_id.product_tmpl_id", "=", product.id),
                ]
            )
            if product.qty_total:
                supplier_stock_records.update(
                    {
                        "partner_loc_id": int(stock_data_local_supplier_location_id)
                        if product.qty_local_stock
                        else int(stock_data_oversea_supplier_location_id),
                        "website_quantity": str(int(product.qty_total))
                        if product.qty_total < 3
                        else "3",
                    }
                )
            else:
                supplier_stock_records.unlink()
        updated_products.update({"update_partner_stock": False})
