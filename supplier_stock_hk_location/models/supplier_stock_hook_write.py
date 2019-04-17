# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.addons.product_offer.models.supplier_stock import SupplierStock


@api.multi
def write(self, vals):
    res = super(SupplierStock, self).write(vals)
    if 'product_id' in vals or 'quantity' in vals or 'partner_loc_id' in vals:
        self._update_prod_tmpl_qty()
    return res


class SupplierStockHookWrite(models.AbstractModel):
    _name = 'supplier.stock.hook.write'
    _desctription = 'Provide hook point for write method'

    def _register_hook(self, cr):
        SupplierStock.write = write
        return super(SupplierStockHookWrite, self)._register_hook(cr)
