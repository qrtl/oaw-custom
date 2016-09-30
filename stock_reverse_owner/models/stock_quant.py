# -*- coding: utf-8 -*-
# Copyright 2016 Rooms For (Hong Kong) Limited T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _update_original_owner_id(self, cr, uid):
        # update quant original_owner_id when installing/upgrading
        cr.execute("""
            UPDATE stock_quant
            SET original_owner_id = owner_id
            WHERE original_owner_id IS null
        """)
