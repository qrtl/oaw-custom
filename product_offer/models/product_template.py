# -*- coding: utf-8 -*-
# Copyright 2017 Rooms For (Hong Kong) Limted T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.addons.decimal_precision import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"


    # this field is added due to kanban view limitation
    list_price_integer = fields.Integer(
        string='Sale Price',
        compute='_get_list_price_integer',
        store=True,
    )
    qty_local_atp = fields.Integer(
        string="Quantity Local ATP",
        compute="_get_qty_info",
        # search="_search_product_quantity",
    )
    qty_reserved = fields.Integer(
        string="Quantity Reserved",
        compute="_get_qty_info",
    )
    qty_overseas = fields.Integer(
        string="Quantity Overseas",
        compute="_get_qty_info",
    )


    @api.multi
    @api.depends('list_price')
    def _get_list_price_integer(self):
        for prod in self:
            prod.list_price_integer = int(prod.list_price)

    def _get_qty_in(self, p_id):
        res = 0.0
        move_obj = self.env['stock.move']
        moves = move_obj.search([
            ('product_id', '=', p_id),
            ('picking_type_code', '=', 'incoming'),
            ('state', '=', 'assigned'),
        ])
        for m in moves:
            res += m.product_uom_qty
        return res

    def _get_qty_reserved(self, p_id):
        res = 0.0
        quant_obj = self.env['stock.quant']
        quants = quant_obj.search([
            '|',
            ('reservation_id', '!=', False),
            ('sale_id', '!=', False),
            ('product_id', '=', p_id),
            ('usage', '=', 'internal')
        ])
        for q in quants:
            res += q.qty
        return res

    def _get_qty_overseas(self, p_id):
        res = 0.0
        supp_stock_obj = self.env['supplier.stock']
        records = supp_stock_obj.search([
            ('product_id', '=', p_id),
        ])
        for rec in records:
            res += rec.quantity
        return res

    @api.multi
    def _get_qty_info(self):
        for prod in self:
            qty_available = 0.0
            qty_in = 0.0
            qty_reserved = 0.0
            qty_overseas = 0.0
            for p in prod.product_variant_ids:
                qty_available += p.qty_available
                qty_in += self._get_qty_in(p.id)
                qty_reserved += self._get_qty_reserved(p.id)
                qty_overseas += self._get_qty_overseas(p.id)
            prod.qty_local_atp = int(qty_available + qty_in)
            prod.qty_reserved = int(qty_reserved)
            prod.qty_overseas = int(qty_overseas)
