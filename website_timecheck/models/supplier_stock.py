# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class SupplierStock(models.Model):
    _inherit = 'supplier.stock'

    @api.multi
    def write(self, vals):
        for ss in self:
            # For Special Price Filter
            if 'price_unit' in vals:
                if ss.price_unit > vals['price_unit']:
                    ss.product_id.product_tmpl_id.sudo().write({
                        'partner_stock_special_offer': fields.Datetime.now(),
                        'partner_stock_retail_currency_price':
                            ss.retail_in_currency,
                        'partner_stock_retail_currency_id': ss.currency_id.id
                    })
            if 'quantity' in vals:
                if ss.quantity < vals['quantity']:
                    ss.product_id.product_tmpl_id.sudo().write({
                        'partner_stock_new_arrival': fields.Datetime.now()
                    })
        return super(SupplierStock, self).write(vals)

    @api.model
    def create(self, vals):
        res = super(SupplierStock, self).create(vals)
        for ss in res:
            if ss.quantity != 0:
                ss.product_id.product_tmpl_id.sudo().write({
                    'partner_stock_new_arrival': fields.Datetime.now()
                })
        return res
