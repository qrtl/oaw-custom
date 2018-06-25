# -*- coding: utf-8 -*-
# Copyright 2017-2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.multi
    def write(self, vals):
        res = super(StockQuant, self).write(vals)
        if 'location_id' in vals or 'product_id' in vals or 'usage' in vals:
            for sq in self:
                sq.product_id.product_tmpl_id.sudo()._get_stock_location()
        return res

    @api.model
    def create(self, vals):
        res = super(StockQuant, self).create(vals)
        if 'location_id' in vals or 'product_id' in vals or 'usage' in vals:
            res.product_id.product_tmpl_id.sudo()._get_stock_location()
        return res

    @api.multi
    def unlink(self):
        products = []
        for sq in self:
            products.append(sq.product_id.product_tmpl_id)
        res = super(StockQuant, self).unlink()
        for product in products:
            product.sudo()._get_stock_location()
        return res
