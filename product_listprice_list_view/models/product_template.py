# -*- coding: utf-8 -*-
# Copyright 2017 Rooms For (Hong Kong) Limted T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"

    stock_cost = fields.Float(
        string="Stock Cost",
        compute='_get_stock_cost',
        digits=dp.get_precision('Product Price'),
    )
    stock_location = fields.Char(
        string="Stock Location",
        compute='_get_stock_location'
    )


    def _get_quant_cost(self, prod_ids):
        quant_obj = self.env['stock.quant']
        quant = quant_obj.search(
            [('product_id', 'in', prod_ids),
             ('usage', '=', 'internal')],
            order='cost',
            limit=1
        )
        if quant:
            return quant.cost
        return 0.0

    def _get_supp_stock_cost(self, prod_ids):
        st_obj = self.env['supplier.stock']
        records = st_obj.search(
            [('product_id', 'in', prod_ids)]
        )
        if records:
            return min(r.price_unit_base for r in records)
        return 0.0

    @api.multi
    def _get_stock_cost(self):
        for pt in self:
            prod_ids = [p.id for p in pt.product_variant_ids]
            quant_cost = self._get_quant_cost(prod_ids)
            supp_stock_cost = self._get_supp_stock_cost(prod_ids)
            pt.stock_cost = min([quant_cost, supp_stock_cost])

    def _get_local_location_name(self, prod_ids):
        quant_obj = self.env['stock.quant']
        quant = quant_obj.search(
            [('product_id', 'in', prod_ids),
             ('usage', '=', 'internal')],
            order='cost',
            limit=1
        )
        return quant.location_id.name

    def _get_overseas_location_name(self, prod_ids):
        ss_obj = self.env['supplier.stock']
        ss_recs = ss_obj.search(
            [('product_id', 'in', prod_ids)]
        )
        lowest_cost = 0.0
        for ss_rec in ss_recs:
            if not lowest_cost or ss_rec.price_unit_base < lowest_cost:
                lowest_cost = ss_rec.price_unit_base
                lowest_cost_ss_rec = ss_rec
        return lowest_cost_ss_rec.partner_loc_id.name

    @api.multi
    def _get_stock_location(self):
        for pt in self:
            prod_ids = [p.id for p in pt.product_variant_ids]
            if pt.local_stock == 'Yes':
                pt.stock_location = self._get_local_location_name(prod_ids)
            elif pt.overseas_stock == 'Yes':
                pt.stock_location = self._get_overseas_location_name(prod_ids)
