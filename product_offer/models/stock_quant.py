# -*- coding: utf-8 -*-
# Copyright 2017 Rooms For (Hong Kong) Limted T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def _update_product_template(self, quant):
        quant.product_id.product_tmpl_id.last_in_date = quant.in_date
        return

    @api.v7
    def _quant_create(self, cr, uid, qty, move, lot_id=False, owner_id=False,
                      src_package_id=False, dest_package_id=False,
                      force_location_from=False, force_location_to=False,
                      context=None):
        quant = super(StockQuant, self)._quant_create(cr, uid, qty, move,
                                                       lot_id, owner_id,
                                                       src_package_id,
                                                       dest_package_id,
                                                       force_location_from,
                                                       force_location_to,
                                                       context)
        self._update_product_template(cr, uid, quant)
        return quant

    @api.multi
    def _update_prod_tmpl_reserved_qty(self):
        prod_tmpls = set()
        for quant in self:
            prod_tmpls.add(quant.product_id.product_tmpl_id)
        for prod_tmpl in prod_tmpls:
            rsvd_qty = 0.0
            for prod in prod_tmpl.product_variant_ids:
                quants = self.search(
                    ['|', ('reservation_id', '!=', False),
                     ('sale_id', '!=', False),
                     ('product_id', '=', prod.id),
                     ('usage', '=', 'internal')]
                )
                for q in quants:
                    rsvd_qty += q.qty
            prod_tmpl.qty_reserved = int(rsvd_qty)
        return

    @api.multi
    def write(self, vals):
        res = super(StockQuant, self).write(vals)
        self._update_prod_tmpl_reserved_qty()
        return res
