# -*- coding: utf-8 -*-
# Copyright 2017-2018 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    sale_order_customer_id = fields.Many2one(
        related='order_id.sale_order_customer_id',
        readonly=True,
        string='Sales Order Customer',
    )

    image_small = fields.Binary(
        'Image',
        related='product_id.product_tmpl_id.image_small',
        readonly=True,
    )
    line_sequence = fields.Integer(
        string="Sequence",
        readonly=True,
    )
