# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    image_small = fields.Binary(
        'Image',
        related='product_id.product_tmpl_id.image_small',
        readonly=True,
    )
    line_sequence = fields.Integer(
        string="Sequence",
        readonly=True,
    )
