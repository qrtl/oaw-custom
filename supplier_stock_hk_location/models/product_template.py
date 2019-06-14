# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    qty_local_own_stock = fields.Integer(
        string='Quantity Local Stock',
        compute='_get_qty_local_stock',
        store=True,
    )
    qty_local_supplier_stock = fields.Integer(
        string='Quantity Local Supplier Stock',
        compute='_get_qty_local_stock',
        store=True,
    )

    @api.multi
    def _get_oversea_retail(self):
        for pt in self:
            if pt.product_variant_ids:
                supplier_stock = self.env['supplier.stock'].sudo().search([
                    ('product_id', '=', pt.product_variant_ids[0].id),
                    ('quantity', '!=', 0),
                    ('hk_location', '=', False)
                ], order='retail_unit_base', limit=1)
                pt.oversea_retail_price = supplier_stock.retail_in_currency
                pt.oversea_retail_currency_id = supplier_stock.currency_id

    @api.multi
    @api.depends('qty_local_stock')
    def _get_qty_local_stock(self):
        for pt in self:
            supplier_local_qty = 0
            if pt.product_variant_ids:
                supplier_stocks = self.env['supplier.stock'].sudo().search([
                    ('product_id', 'in', pt.product_variant_ids.ids),
                    ('quantity', '!=', 0),
                    ('hk_location', '=', True)
                ])
                for ss in supplier_stocks:
                    supplier_local_qty += ss.quantity
            pt.qty_local_own_stock = pt.qty_local_stock - supplier_local_qty
            pt.qty_local_supplier_stock = supplier_local_qty

    @api.multi
    def _get_stock_location(self):
        for pt in self:
            prod_ids = [p.id for p in pt.product_variant_ids]
            pt.stock_location = False
            pt.stock_leadtime = '/'
            if pt.overseas_stock == 'Yes' or pt.qty_local_supplier_stock > 0:
                pt.stock_location, supp_lt, pt.partner_note2,\
                pt.retail_of_cheapest, pt.curr_of_cheapest = \
                    self._get_overseas_location_name(prod_ids)
                pt.stock_leadtime = str(supp_lt) + ' day(s)'
            if pt.local_stock == 'Yes' and pt.qty_local_own_stock > 0:
                local_location_name = self._get_local_location_name(prod_ids)
                if pt.overseas_stock == 'Yes' or pt.qty_local_supplier_stock > 0:
                    if local_location_name:
                        pt.stock_location += ', ' + local_location_name
                else:
                    pt.stock_location = local_location_name
                    pt.stock_leadtime = '0 day(s)'
