# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.tests.common import TransactionCase


class TestChannelFeatures(TransactionCase):
    def setUp(self):
        super(TestChannelFeatures, self).setUp()
        test_partner = self.env["res.partner"].create(
            {"name": "Test Partner", "email": "test@example.com"}
        )

        self.test_channel = self.env["mail.channel"].create(
            {
                "name": "Test",
                "description": "Description",
                "alias_name": "test",
                "public": "public",
            }
        )
        self.sale_order_01 = self.env["sale.order"].create(
            {"partner_id": test_partner.id}
        )
        self.sale_order_02 = self.env["sale.order"].create(
            {"partner_id": test_partner.id}
        )
        self.sale_order_01.action_confirm()
        self.sale_order_02.action_confirm()

    def test_message_post(self):
        message = "<p>Hi, please find your sales orders "

        msg = self.test_channel.message_post(
            body=message + str(self.sale_order_01.name + " " + self.sale_order_02.name)
        )

        # Creates Order Reference link
        message += str(
            '<a href="#" data-oe-id="'
            + str(self.sale_order_01.id)
            + '" data-oe-model="sale.order">'
            + self.sale_order_01.name
            + "</a>  "
        )
        message += str(
            '<a href="#" data-oe-id="'
            + str(self.sale_order_02.id)
            + '" data-oe-model="sale.order">'
            + self.sale_order_02.name
            + "</a> </p>"
        )

        self.assertEqual(msg.body, message)
