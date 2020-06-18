# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common, tagged


@tagged("-at_install", "post_install")
class SaleOrderLineDisableCheckAvailability(common.TransactionCase):
    def setUp(self):
        super(SaleOrderLineDisableCheckAvailability, self).setUp()
        self.service_product = self.env.ref("sale.advance_product_0")
        self.out_of_stockable_product = self.env.ref("product.product_product_4d")

    def test_00_create_order_line(self):
        so = self.env["sale.order"].create({"partner_id": 1})
        service_product_line = self.env["sale.order.line"].create(
            {"order_id": so.id, "name": "test", "product_id": self.service_product.id}
        )
        # additional variant to test correct ignoring when mismatch values
        out_of_stockable_product = self.env["sale.order.line"].create(
            {
                "order_id": so.id,
                "name": "test",
                "product_id": self.out_of_stockable_product.id,
            }
        )
        self.assertEqual(
            service_product_line._onchange_product_id_check_availability(), {}
        )
        self.assertEqual(
            out_of_stockable_product._onchange_product_id_check_availability(), {}
        )
