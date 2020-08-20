# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import re

from odoo import api, models


class MailChannel(models.Model):
    _inherit = "mail.channel"

    @api.multi
    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, **kwargs):
        list_value = kwargs.get("body").split()
        keywords = re.findall(r"\w+", " ".join(list_value))
        for keyword in keywords:
            sale_order_id = self.env["sale.order"].search(
                [("name", "=", keyword)], limit=1
            )
            if sale_order_id:
                order_href_link = (
                    '<a href="#" data-oe-id='
                    + str(sale_order_id.id)
                    + ' data-oe-model="sale.order">'
                    + sale_order_id.name
                    + "</a> "
                )
                kwargs.update(
                    {"body": kwargs.get("body").replace(keyword, str(order_href_link))}
                )
        return super(MailChannel, self).message_post(**kwargs)
