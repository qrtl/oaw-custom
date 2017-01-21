# -*- coding: utf-8 -*-
# Copyright 2017 Rooms For (Hong Kong) Limted T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"

    stock_cost = fields.Float(
        string="Stock Cost",
#        compute='_get_stock_cost',
        digits=dp.get_precision('Product Price'),
    )


    def _get_quant_cost(self, pt):
        quant_obj = self.env['stock.quant']
        prod_ids = [p.id for p in pt.product_variant_ids]
        quant = quant_obj.search(
            [('product_id', 'in', prod_ids),
             ('usage', '=', 'internal')],
            order='cost',
            limit=1
        )
        if quant:
            return quant.cost
        else:
            return 0.0

    def _get_supp_stock_cost(self):
        return

    @api.multi
    def _get_stock_cost_(self):
        for pt in self:
            quant_cost = self._get_quant_cost(pt)
            supp_stock_cost = self._get_supp_stock_cost(pt)
        return
