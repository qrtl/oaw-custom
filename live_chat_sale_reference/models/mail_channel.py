# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import re

from odoo import api, models


class MailChannel(models.Model):
    _inherit = "mail.channel"

    @api.multi
    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, message_type="notification", **kwargs):
        keywords = re.findall(r"\w+", kwargs.get("body"))
        sale_orders = self.env["sale.order"].search([("name", "in", keywords)])
        for order in sale_orders:
            kwargs.update(
                {
                    "body": kwargs.get("body").replace(
                        order.name,
                        str(
                            '<a href="#" data-oe-id='
                            + str(order.id)
                            + ' data-oe-model="sale.order">'
                            + order.name
                            + "</a> "
                        ),
                    )
                }
            )
        return super(MailChannel, self).message_post(
            message_type=message_type, **kwargs
        )
