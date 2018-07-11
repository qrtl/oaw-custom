# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    movement = fields.Char(
       'Movement',
        readonly=True,
        related="product_id.product_tmpl_id.movement",
    )
    material = fields.Char(
        'Material',
        readonly=True,
        related="product_id.product_tmpl_id.material",
    )
