# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class StockReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    @api.model
    def default_get(self, fields):
        return_pick = super(StockReturnPicking, self).default_get(fields)
        if 'product_return_moves' in return_pick:
            return_moves = return_pick['product_return_moves']
            for move in return_moves:
                if self.env['product.product'].browse(move['product_id']).\
                        product_tmpl_id.categ_id.enforce_qty_1:
                    quant = self.env['stock.quant'].search(
                        [('history_ids', 'in', move['move_id'])])
                    if quant and quant[0].lot_id:
                        move['lot_id'] = quant[0].lot_id.id
        return return_pick
