# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    consignment_supplier_stock_ids = fields.One2many(
        comodel_name='supplier.stock',
        inverse_name='order_line_id',
        readonly=True,
    )

    @api.multi
    def create_update_consignment_partner_stock(self):
        for order_line in self:
            supplier_location = self.env['supplier.location'].search([
                ('owner_id', '=', order_line.order_id.partner_id.id),
                ('active', '=', True)
            ], limit=1)
            vals = {
                'partner_id': order_line.order_id.partner_id.id,
                'partner_loc_id': supplier_location.id,
                'product_id': order_line.product_id.id,
                'prod_cat_selection': order_line.product_id.categ_id.id,
                'quantity': order_line.product_uom_qty,
                'price_unit': order_line.purchase_price,
                'retail_in_currency': order_line.price_unit,
                'currency_id': order_line.order_id.pricelist_id.currency_id.id,
                'order_line_id': order_line.id,
            }
            if order_line.consignment_supplier_stock_ids:
                order_line.consignment_supplier_stock_ids.update(vals)
                _logger.info(
                    'Updated Partner Stock Record(s): %s' % order_line.consignment_supplier_stock_ids.ids)
            else:
                created_supplier_stock = self.env['supplier.stock'].create(
                    vals)
                _logger.info(
                    'Created Partner Stock Record: %s' % created_supplier_stock.id)

    @api.multi
    def unlink_consignment_partner_stock(self):
        for order_line in self:
            _logger.info(
                'Deleted Partner Stock Record: %s' % order_line.consignment_supplier_stock_ids.ids)
            order_line.consignment_supplier_stock_ids.unlink()
