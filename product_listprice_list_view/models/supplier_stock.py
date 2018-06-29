# -*- coding: utf-8 -*-
# Copyright 2017-2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class SupplierStock(models.Model):
    _inherit = "supplier.stock"

    @api.multi
    def write(self, vals):
        res = super(SupplierStock, self).write(vals)
        if 'partner_loc_id' in vals or 'product_id' in vals:
            for ss in self:
                ss.product_id.product_tmpl_id.sudo()._get_stock_location()
        return res

    @api.model
    def create(self, vals):
        res = super(SupplierStock, self).create(vals)
        if 'partner_loc_id' in vals or 'product_id' in vals:
            res.product_id.product_tmpl_id.sudo()._get_stock_location()
        return res

    @api.multi
    def unlink(self):
        products = []
        for ss in self:
            products.append(ss.product_id.product_tmpl_id)
        res = super(SupplierStock, self).unlink()
        for  product in products:
            product.sudo()._get_stock_location()
        return res
