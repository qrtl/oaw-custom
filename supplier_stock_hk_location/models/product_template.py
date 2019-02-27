# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

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
