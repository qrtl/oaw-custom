# Copyright 2019 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivery_status = fields.Selection(
        [
            ("waiting", "To Deliver"),
            ("delivered", "Delivered"),
            ("partial", "Partially Delivered"),
            ("no", "Nothing to Deliver"),
        ],
        string="Delivery Status",
        compute="_compute_delivery_status",
        store=True,
    )

    @api.depends("state", "order_line.qty_delivered")
    def _compute_delivery_status(self):
        for order in self:
            order.delivery_status = "no"
            deliver_lines = order.order_line.filtered(
                lambda l: l.product_id.type != "service"
            )
            if order.state in ("sale", "done") and deliver_lines:
                order.delivery_status = "waiting"
                all_delivered = True
                delivered_qty = False
                for line in deliver_lines:
                    if line.product_uom_qty != line.qty_delivered:
                        all_delivered = False
                    if line.qty_delivered:
                        delivered_qty = True
                if delivered_qty:
                    order.delivery_status = "delivered" if all_delivered else "partial"
