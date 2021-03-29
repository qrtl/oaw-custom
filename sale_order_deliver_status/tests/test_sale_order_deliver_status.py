# Copyright 2021 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time

from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestSaleOrderDeliverStatus(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleOrderDeliverStatus, cls).setUpClass()
        cls.product = cls.env["product.product"].create({"name": "Product A"})
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.env.ref("base.res_partner_1").id,
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": cls.product.id,
                            "name": "1 Product",
                            "price_unit": 100.0,
                        },
                    ),
                ],
            }
        )
        cls.order.action_confirm()
        cls.bank_journal = cls.env["account.journal"].create(
            {"name": "Bank", "type": "bank", "code": "TEST0001"}
        )
        cls.payment_method_manual_in = cls.env.ref(
            "account.account_payment_method_manual_in"
        )

    def test_order_status(self):
        # Validate Delivery
        picking = self.order.picking_ids[0]
        for ml in picking.move_line_ids:
            ml.qty_done = ml.product_uom_qty
        picking.action_done()
        # Create first invoice
        invoice_ids = self.order.action_invoice_create()
        invoice1 = self.env["account.invoice"].browse(invoice_ids)
        invoice1.action_invoice_open()
        self.assertEqual(self.order.order_status, "open")
        # Pay Invoice
        ctx = {"active_model": "account.invoice", "active_ids": [invoice1.id]}
        register_payments = (
            self.env["account.register.payments"]
            .with_context(active_model="account.invoice")
            .with_context(ctx)
            .create(
                {
                    "payment_date": time.strftime("%Y") + "-07-15",
                    "journal_id": self.bank_journal.id,
                    "payment_method_id": self.payment_method_manual_in.id,
                }
            )
        )
        register_payments.create_payments()
        self.assertEqual(self.order.order_status, "done")
