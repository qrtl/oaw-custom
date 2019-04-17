# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    def _update_prod_tmpl_qty_local_stock(self):
        for move in self:
            prod_tmpl = move.product_tmpl_id
            qty_in = self._get_qty_in(prod_tmpl.id)

            local_sp_qty = 0.0
            for prod in prod_tmpl.product_variant_ids:
                records = self.env['supplier.stock'].sudo().search([
                    ('product_id', '=', prod.id),
                    ('hk_location', '=', True)
                ])
                for r in records:
                    local_sp_qty += r.quantity

            if prod_tmpl.qty_local_stock != int(prod_tmpl.qty_available +
                                                qty_in + local_sp_qty):
                prod_tmpl.qty_local_stock = int(prod_tmpl.qty_available +
                                                qty_in + local_sp_qty)
        return
