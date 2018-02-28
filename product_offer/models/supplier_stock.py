# -*- coding: utf-8 -*-
# Copyright 2017 Rooms For (Hong Kong) Limted T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class SupplierStock(models.Model):
    _inherit = "supplier.stock"

    @api.model
    def create(self, vals):
        res = super(SupplierStock, self).create(vals)
        product = self.env['product.product'].browse(
            vals.get('product_id', False))
        if product:
            product.product_tmpl_id.sudo().write({
                'qty_overseas': int(vals.get('quantity', 0.0))
            })
        return res

    @api.multi
    def _update_prod_tmpl_qty_overseas(self):
        prod_tmpls = set()
        for st in self:
            prod_tmpls.add(st.product_id.product_tmpl_id)
        for prod_tmpl in prod_tmpls:
            ovrs_qty = 0.0
            for prod in prod_tmpl.product_variant_ids:
                records = self.search(
                    [('product_id', '=', prod.id)]
                )
                for r in records:
                    ovrs_qty += r.quantity
            prod_tmpl.qty_overseas = int(ovrs_qty)
        return

    @api.multi
    def write(self, vals):
        res = super(SupplierStock, self).write(vals)
        if 'product_id' in vals or 'quantity' in vals:
            self._update_prod_tmpl_qty_overseas()
        return res

    @api.multi
    def unlink(self):
        for st in self:
            st.product_id.product_tmpl_id.qty_overseas -= int(st.quantity)
        return super(SupplierStock, self).unlink()
