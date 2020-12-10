# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import SavepointCase, tagged


@tagged("post_install", "-at_install")
class TestMailChannelSaleOrderLink(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        test_partner = cls.env["res.partner"].create(
            {"name": "Test Partner", "email": "test@example.com"}
        )

        cls.test_channel = cls.env["mail.channel"].create(
            {
                "name": "Test",
                "description": "Description",
                "alias_name": "test",
                "public": "public",
            }
        )
        cls.sale_order_01 = cls.env["sale.order"].create(
            {"partner_id": test_partner.id}
        )
        cls.sale_order_02 = cls.env["sale.order"].create(
            {"partner_id": test_partner.id}
        )
        cls.sale_order_01.action_confirm()
        cls.sale_order_02.action_confirm()

    def test_message_post(self):
        message = " ".join([self.sale_order_01.name, self.sale_order_02.name])
        posted_message = self.test_channel.message_post(body=message)
        converted_message = (
            '<a href="#" data-oe-id="%s" data-oe-model="sale.order">%s</a> '
            '<a href="#" data-oe-id="%s" data-oe-model="sale.order">%s</a>'
            % (
                str(self.sale_order_01.id),
                self.sale_order_01.name,
                str(self.sale_order_02.id),
                self.sale_order_02.name,
            )
        )
        self.assertEqual(posted_message.body, converted_message)
