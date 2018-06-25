# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp import workflow

class saleOrderLineSupplierAccess(models.Model):
    _inherit = 'sale.order.line'


    movement = fields.Char(
       'Movement',
        readonly=True,
        related="product_id.product_tmpl_id.movement"
    )

    material = fields.Char(
        'Material',
        readonly=True,
        related="product_id.product_tmpl_id.material"
    )