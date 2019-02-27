# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def _update_overseas_info(self):
        prod_tmpls = set()
        for pp in self:
            prod_tmpls.add(pp.product_tmpl_id)
        for prod_tmpl in prod_tmpls:
            ovrs_qty = 0.0
            for prod in prod_tmpl.product_variant_ids:
                records = self.env['supplier.stock'].sudo().search([
                    ('product_id', '=', prod.id),
                    ('hk_location', '=', False)
                ])
                for r in records:
                    ovrs_qty += r.quantity
            prod_tmpl.sudo().write({
                'qty_overseas': int(ovrs_qty)
            })
            prod_tmpl.sudo()._get_stock_location()

    @api.multi
    def _update_prod_tmpl_qty(self):
        prod_tmpls = set()
        for pp in self:
            prod_tmpls.add(pp.product_tmpl_id)
        for prod_tmpl in prod_tmpls:
            local_qty = 0.0
            ovrs_qty = 0.0
            for prod in prod_tmpl.product_variant_ids:
                records = self.env['supplier.stock'].sudo().search([
                    ('product_id', '=', prod.id)
                ])
                for r in records:
                    if r.hk_locaton:
                        local_qty += r.quantity
                    else:
                        ovrs_qty += r.quantity
            prod_tmpl.sudo().write({
                'qty_local_stock': int(local_qty) + prod_tmpl.qty_available,
                'qty_overseas': int(ovrs_qty)
            })
            prod_tmpl.sudo()._get_stock_location()
