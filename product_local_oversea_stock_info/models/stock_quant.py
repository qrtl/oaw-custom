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
    cost = fields.Float(
        string='Unit Cost',
    )

    @api.model
    def _update_product_last_in_date(self):
        for quant in self:
            quant.product_id.product_tmpl_id.last_in_date = quant.in_date

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
        if 'location_id' in vals or 'product_id' in vals or 'usage' in vals:
            for sq in self:
                sq.product_id.product_tmpl_id.sudo()._get_stock_location()
        return res

    @api.model
    def create(self, vals):
        res = super(StockQuant, self).create(vals)
        self._update_product_last_in_date()
        if 'location_id' in vals or 'product_id' in vals or 'usage' in vals:
            res.product_id.product_tmpl_id.sudo()._get_stock_location()
        return res

    @api.multi
    def unlink(self):
        products = []
        for sq in self:
            products.append(sq.product_id.product_tmpl_id)
        res = super(StockQuant, self).unlink()
        for product in products:
            product.sudo()._get_stock_location()
        return res
