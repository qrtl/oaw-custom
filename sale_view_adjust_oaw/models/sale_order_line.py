# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    note_client_name = fields.Char(
        string="Note Client Name",
    )
    note_client_price = fields.Char(
        string="Note Client Price",
    )
    image_small = fields.Binary(
        'Image',
        related='product_id.product_tmpl_id.image_small',
        readonly=True,
    )
