# -*- coding: utf-8 -*-
# Copyright 2017 Rooms For (Hong Kong) Limted T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.addons.decimal_precision import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"


    list_price_integer = fields.Integer(
        string='Sale Price',
        compute='_get_list_price_integer',
        store=True,
    )

    qty_local_atp = fields.Float(
        string="Quantity Local ATP",
        compute="_product_local_atp",
        # search="_search_product_quantity",
        digits=dp.get_precision('Product Unit of Measure'),
    )

    @api.multi
    @api.depends('list_price')
    def _get_list_price_integer(self):
        for prod in self:
            prod.list_price_integer = int(prod.list_price)

    def _get_qty_in(self, p_id):
        qty_in = 0
        move_obj = self.env['stock.move']
        moves = move_obj.search([
            ('product_id', '=', p_id),
            ('picking_type_code', '=', 'incoming'),
            ('state', '=', 'assigned'),
        ])
        for m in moves:
            qty_in += m.product_uom_qty
        return qty_in

    @api.multi
    def _product_local_atp(self):
        for prod in self:
            qty_available = 0
            qty_in = 0
            for p in prod.product_variant_ids:
                qty_available += p.qty_available
                qty_in += self._get_qty_in(p.id)
            prod.qty_local_atp = qty_available + qty_in
