# -*- coding: utf-8 -*-
# Copyright 2017 Rooms For (Hong Kong) Limted T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class StockQuant(models.Model):
    _inherit = "stock.quant"


    @api.model
    def _update_product_template(self, quant):
        pt_obj = self.env['product.template']
        pt_obj.browse([quant.product_id.product_tmpl_id.id]).write(
            {'last_in_date': quant.in_date}
        )

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
