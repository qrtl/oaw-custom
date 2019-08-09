# -*- coding: utf-8 -*-
# Copyright 2017-2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"


    advertise = fields.Boolean(
        default=False
    )
    net_profit = fields.Float(
        string="Net Profit",
        digits=dp.get_precision('Product Price'),
        compute='_compute_net_profit',
        readonly=True,
        store=True
    )
    net_profit_pct = fields.Float(
        string="Net Profit Percent",
        digits=dp.get_precision('Discount'),
        compute='_compute_net_profit',
        readonly=True
    )
    stock_cost = fields.Float(
        string="Stock Cost",
        compute='_get_stock_cost',
        digits=dp.get_precision('Product Price'),
    )
    stock_location = fields.Char(
        string="Stock Location",
        compute='_get_stock_location',
        store=True,
    )
    stock_leadtime = fields.Char(
        string='Stock Lead Time',
        compute='_get_stock_location',
    )
    partner_note2 = fields.Text(
        string = 'Partner Note',
        compute='_get_stock_location',
    )
    retail_of_cheapest =  fields.Float(
        string="Stock Cost",
        compute='_get_stock_location',
        digits=dp.get_precision('Product Price'),
    )
    curr_of_cheapest = fields.Char(
        string="Currency",
        compute='_get_stock_location',
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
        return False

    def _get_supp_stock_cost(self, prod_ids):
        st_obj = self.env['supplier.stock']
        records = st_obj.search(
            [('product_id', 'in', prod_ids),
             ('quantity', '>', 0)]
        )
        if records:
            return min(r.price_unit_base for r in records)
        return False

    @api.multi
    def _get_stock_cost(self):
        for pt in self:
            prod_ids = [p.id for p in pt.product_variant_ids]
            # print(prod_ids)
            supp_stock_cost = self._get_supp_stock_cost(prod_ids)
            if supp_stock_cost:
                pt.stock_cost = supp_stock_cost
                continue
            quant_cost = self._get_quant_cost(prod_ids)
            if quant_cost:
                pt.stock_cost = quant_cost
                continue
            pt.stock_cost = pt.standard_price



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
        ss_recs = ss_obj.sudo().search([
            ('product_id', 'in', prod_ids),
            ('quantity', '>', 0)
        ])
        lowest_cost = 0.0
        lowest_cost_ss_rec = False
        for ss_rec in ss_recs:
            if not lowest_cost or ss_rec.price_unit_base < lowest_cost:
                lowest_cost = ss_rec.price_unit_base
                lowest_cost_ss_rec = ss_rec
        if lowest_cost_ss_rec:
            loc = lowest_cost_ss_rec.partner_loc_id.name
            supp_lt = lowest_cost_ss_rec.supplier_lead_time
            partner_note2 = lowest_cost_ss_rec.partner_note
            retail_of_cheapest = lowest_cost_ss_rec.retail_in_currency
            curr_of_cheapest = lowest_cost_ss_rec.currency_id.name

            return loc, supp_lt, partner_note2, retail_of_cheapest, curr_of_cheapest
        else:
            return False, False, False, False, False

    @api.multi
    def _get_stock_location(self):
        for pt in self:
            prod_ids = [p.id for p in pt.product_variant_ids]
            pt.stock_location = False
            pt.stock_leadtime = '/'
            if pt.overseas_stock == 'Yes':
                pt.stock_location, supp_lt, pt.partner_note2,\
                pt.retail_of_cheapest, pt.curr_of_cheapest = \
                    self._get_overseas_location_name(prod_ids)
                pt.stock_leadtime = str(supp_lt) + ' day(s)'
            if pt.local_stock == 'Yes':
                local_location_name = self._get_local_location_name(prod_ids)
                if pt.overseas_stock == 'Yes':
                    if local_location_name:
                        pt.stock_location += ', ' + local_location_name
                else:
                    pt.stock_location = local_location_name
                    pt.stock_leadtime = '0 day(s)'

    @api.multi
    @api.depends('net_price', 'stock_cost')
    def _compute_net_profit(self):
        for pt in self:
            if pt.net_price == 0.0 or pt.stock_cost == 0.0:
                pt.net_profit = 0.00
                pt.net_profit_pct = 0.00
            else:
                pt.net_profit = pt.net_price - pt.stock_cost
                pt.net_profit_pct = (pt.net_price / pt.stock_cost) * 100 - 100
        return
