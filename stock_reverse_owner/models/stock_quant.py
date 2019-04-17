# -*- coding: utf-8 -*-
# Copyright 2016 Rooms For (Hong Kong) Limited T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    repair = fields.Boolean(
        string='Repair',
        related='location_id.is_repair_location',
        store=True
    )


    def _update_original_owner_id(self, cr, uid):
        # update quant original_owner_id when installing/upgrading
        cr.execute("""
            UPDATE stock_quant
            SET original_owner_id = owner_id
            WHERE original_owner_id IS null
        """)


    def _update_repair(self, cr, uid):
        # update quant repair when installing/upgrading
        cr.execute("""
            UPDATE stock_quant q
            SET repair = TRUE
            FROM stock_location l
            WHERE q.location_id = l.id
                AND l.is_repair_location = TRUE
        """)
