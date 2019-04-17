# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    qty_local_own_stock = fields.Integer(
        string='Quantity Local Stock',
        compute='_get_qty_local_own_stock',
        store=True,
    )

    @api.multi
    def _get_oversea_retail(self):
        for pt in self:
            if pt.product_variant_ids:
                supplier_stock = self.env['supplier.stock'].sudo().search([
                    ('product_id', '=', pt.product_variant_ids[0].id),
                    ('quantity', '!=', 0),
                    ('hk_location', '=', False)
                ], order='retail_unit_base', limit=1)
                pt.oversea_retail_price = supplier_stock.retail_in_currency
                pt.oversea_retail_currency_id = supplier_stock.currency_id

    @api.multi
    @api.depends('qty_local_stock')
    def _get_qty_local_own_stock(self):
        for pt in self:
            if pt.product_variant_ids:
                supplier_local_qty = 0
                supplier_stocks = self.env['supplier.stock'].sudo().search([
                    ('product_id', 'in', pt.product_variant_ids.ids),
                    ('quantity', '!=', 0),
                    ('hk_location', '=', True)
                ])
                for ss in supplier_stocks:
                    supplier_local_qty += ss.quantity
            pt.qty_local_own_stock = pt.qty_local_stock - supplier_local_qty
