# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    image_small = fields.Binary(
        'Image',
        related='product_id.product_tmpl_id.image_small',
    )
