# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import re

from odoo import api, models


class MailChannel(models.Model):
    _inherit = "mail.channel"

    @api.multi
    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, message_type="notification", **kwargs):
        # Split the message by spacing
        keywords = re.split('\s+', kwargs.get("body"))
        sale_orders = self.env["sale.order"].search([("name", "in", keywords)])
        for order in sale_orders:
            kwargs.update(
                {
                    "body": kwargs.get("body").replace(
                        order.name,
                        '<a href="#" data-oe-id="%s" data-oe-model="sale.order">%s</a> ' % (str(order.id), order.name)
                    )
                }
            )
        return super(MailChannel, self).message_post(
            message_type=message_type, **kwargs
        )
