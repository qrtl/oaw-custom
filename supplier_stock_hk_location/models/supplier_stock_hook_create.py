# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from openerp.addons.product_offer.models.supplier_stock import SupplierStock


@api.model
def create(self, vals):
    res = super(SupplierStock, self).create(vals)
    product = self.env['product.product'].browse(
        vals.get('product_id', False))
    location = self.env['supplier.stock'].browse(
        vals.get('partner_loc_id', False))
    if product:
        if not location.hk_location:
            product.product_tmpl_id.sudo().write({
                'qty_overseas': product.product_tmpl_id.qty_overseas + int(
                vals.get('quantity', 0.0))
            })
        else:
            product.product_tmpl_id.sudo().write({
                'qty_local_stock': product.product_tmpl_id.qty_available + int(
                    vals.get('quantity', 0.0))
            })
    return res


class SupplierStockHookCreate(models.AbstractModel):
    _name = 'supplier.stock.hook.create'
    _desctription = 'Provide hook point for create method'

    def _register_hook(self, cr):
        SupplierStock.create = create
        return super(SupplierStockHookCreate, self)._register_hook(cr)
