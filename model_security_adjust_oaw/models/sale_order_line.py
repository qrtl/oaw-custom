# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    material = fields.Char(
        string="Material",
        related="product_id.product_tmpl_id.material",
        readonly=True,
    )
    movement = fields.Char(
        string="Movement",
        related="product_id.product_tmpl_id.movement",
        readonly=True,
    )
