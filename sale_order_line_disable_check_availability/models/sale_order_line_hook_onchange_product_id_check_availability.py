# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models
from odoo.addons.sale_stock.models.sale_order import SaleOrderLine


# Monkey Patching
# Overwrite the original _onchange_product_id_check_availability
# i.e. https://github.com/odoo/odoo/blob/12.0/addons/sale_stock/models/sale_order.py#L275-L305
@api.onchange('product_uom_qty', 'product_uom', 'route_id')
def _onchange_product_id_check_availability(self):
    # if not self.product_id or not self.product_uom_qty or not self.product_uom:
    #     self.product_packaging = False
    #     return {}
    # if self.product_id.type == 'product':
    #     precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
    #     product = self.product_id.with_context(
    #         warehouse=self.order_id.warehouse_id.id,
    #         lang=self.order_id.partner_id.lang or self.env.user.lang or 'en_US'
    #     )
    #     product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
    #     if float_compare(product.virtual_available, product_qty, precision_digits=precision) == -1:
    #         is_available = self._check_routing()
    #         if not is_available:
    #             message =  _('You plan to sell %s %s of %s but you only have %s %s available in %s warehouse.') % \
    #                     (self.product_uom_qty, self.product_uom.name, self.product_id.name, product.virtual_available, product.uom_id.name, self.order_id.warehouse_id.name)
    #             # We check if some products are available in other warehouses.
    #             if float_compare(product.virtual_available, self.product_id.virtual_available, precision_digits=precision) == -1:
    #                 message += _('\nThere are %s %s available across all warehouses.\n\n') % \
    #                         (self.product_id.virtual_available, product.uom_id.name)
    #                 for warehouse in self.env['stock.warehouse'].search([]):
    #                     quantity = self.product_id.with_context(warehouse=warehouse.id).virtual_available
    #                     if quantity > 0:
    #                         message += "%s: %s %s\n" % (warehouse.name, quantity, self.product_id.uom_id.name)
    #             warning_mess = {
    #                 'title': _('Not enough inventory!'),
    #                 'message' : message
    #             }
    #             return {'warning': warning_mess}
    return {}

class SaleOrderLineHookOnchangeProductIdCheckAvailability(models.AbstractModel):
    _name = "sale.order.line.hook.onchange.product.id.check.availability"
    _description = "Provide hook point for _onchange_product_id_check_availability method"

    def _register_hook(self):
        SaleOrderLine._onchange_product_id_check_availability = _onchange_product_id_check_availability
        return super(SaleOrderLineHookOnchangeProductIdCheckAvailability,
                     self)._register_hook()
