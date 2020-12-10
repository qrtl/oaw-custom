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

    def test_01_message_post(self):
        message = " ".join([self.sale_order_01.name, self.sale_order_02.name])
        posted_message = self.test_channel.message_post(body=message)
        sale_order_01_link = (
            '<a href="#" data-oe-id="%s" data-oe-model="sale.order">%s</a>'
            % (str(self.sale_order_01.id), self.sale_order_01.name,)
        )
        sale_order_02_link = (
            '<a href="#" data-oe-id="%s" data-oe-model="sale.order">%s</a>'
            % (str(self.sale_order_02.id), self.sale_order_02.name,)
        )
        self.assertTrue(sale_order_01_link in posted_message.body)
        self.assertTrue(sale_order_02_link in posted_message.body)
