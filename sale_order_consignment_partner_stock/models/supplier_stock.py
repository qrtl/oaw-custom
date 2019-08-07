# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class SupplierStock(models.Model):
    _inherit = 'supplier.stock'

    order_line_id = fields.Many2one(
        'sale.order.line',
        string='Order Reference',
        ondelete='cascade',
        readonly=True,
    )
    order_id = fields.Many2one(
        related='order_line_id.order_id',
        string='Order Reference',
        readonly=True,
    )
    pricelist_id = fields.Many2one(
        related='order_line_id.order_id.pricelist_id',
        string='Pricelist',
        readonly=True,
    )
    order_partner_id = fields.Many2one(
        related='order_line_id.order_id.partner_id',
        string='Customer',
        readonly=True,
    )
    order_price_unit = fields.Float(
        related='order_line_id.price_unit',
        string='Sales Retail',
    )
    order_line_product_uom_qty = fields.Float(
        related='order_line_id.product_uom_qty',
        string='Qty',
    )
    order_price_base_unit = fields.Float(
        compute='_compute_order_price_base_unit',
        string='Sales HKD Retail',
    )
    order_line_margin = fields.Float(
        compute='_compute_order_line_margin',
        string='Margin',
    )

    @api.multi
    def _compute_order_price_base_unit(self):
        company_curr = self.env.user.company_id.currency_id                
        for supplier_stock in self:
            if supplier_stock.order_price_base_unit and supplier_stock.pricelist_id:
                supplier_stock.order_price_base_unit = supplier_stock.pricelist_id.currency_id.compute(
                    supplier_stock.order_price_base_unit, company_curr)

    @api.multi
    def _compute_order_line_margin(self):
        for supplier_stock in self:
            if supplier_stock.order_line_id:
                supplier_stock.order_line_margin = supplier_stock.order_line_id.price_subtotal - \
                    supplier_stock.order_line_id.purchase_price
