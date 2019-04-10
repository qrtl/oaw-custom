# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class StockQuant(models.Model):
    _inherit = "stock.quant"

    usage = fields.Selection(
        related='location_id.usage',
        string='Location Type',
        readonly=True,
        store=True,
    )

    @api.model
    def _update_product_last_in_date(self, quant):
        quant.product_id.product_tmpl_id.last_in_date = quant.in_date
        return

    @api.model
    def create(self, vals):
        res = super(StockQuant, self).create(vals)
        self._update_product_last_in_date()
        return res

    @api.multi
    def _update_prod_tmpl_reserved_qty(self):
        prod_tmpls = set()
        for quant in self:
            if not quant.id:
                return
            prod_tmpls.add(quant.product_id.product_tmpl_id)
        for prod_tmpl in prod_tmpls:
            rsvd_qty = 0.0
            for prod in prod_tmpl.product_variant_ids:
                quants = self.search([
                    ('product_id', '=', prod.id),
                    ('usage', '=', 'internal')
                ])
                for q in quants:
                    rsvd_qty += q.reserved_quantity
            if prod_tmpl.qty_reserved != int(rsvd_qty):
                prod_tmpl.qty_reserved = int(rsvd_qty)
        return

    @api.multi
    def write(self, vals):
        res = super(StockQuant, self).write(vals)
        self._update_prod_tmpl_reserved_qty()
        return res
