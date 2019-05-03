# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_show_details(self):
        res = super(StockMove, self).action_show_details()
        res['context'].update({
            'show_purchase_fields': self.picking_type_id.code == 'incoming'
                                    and not self.origin_returned_move_id
        })
        return res
