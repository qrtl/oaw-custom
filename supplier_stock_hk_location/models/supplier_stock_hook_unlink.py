# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.addons.product_offer.models.supplier_stock import SupplierStock


@api.multi
def unlink(self):
    for ss in self:
        if not ss.hk_location:
            qty_overseas = ss.product_id.product_tmpl_id.qty_overseas - \
                           int(ss.quantity)
            ss.product_id.product_tmpl_id.sudo().write({
                'qty_overseas': qty_overseas
            })
        else:
            qty_local_stock = \
                ss.product_id.product_tmpl_id.qty_local_stock - int(
                    ss.quantity)
            ss.product_id.product_tmpl_id.sudo().write({
                'qty_local_stock': qty_local_stock
            })
    return super(SupplierStock, self).unlink()


class SupplierStockHookUnlink(models.AbstractModel):
    _name = 'supplier.stock.hook.unlink'
    _desctription = 'Provide hook point for unlink method'

    def _register_hook(self, cr):
        SupplierStock.unlink = unlink
        return super(SupplierStockHookUnlink, self)._register_hook(cr)
