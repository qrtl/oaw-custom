# -*- coding: utf-8 -*-
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_description = fields.Char(
        string = 'Product Name',
        related = 'product_id.name'
    )

    order_partner_name = fields.Char(
        string='Product Name',
        related='order_id.partner_id.name'
    )

    subtotal_hkd = fields.Float(
        string="Subtotal in HKD",
        digits=dp.get_precision('Product Price'),
        readonly=True,
        store=True
    )