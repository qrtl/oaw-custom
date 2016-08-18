# -*- coding: utf-8 -*-
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016 Rooms For (Hong Kong) Limited T/A OSCG
#    <https://www.odoo-asia.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from openerp import models, api


class StockReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    @api.model
    def default_get(self, fields):
        return_pick = super(StockReturnPicking, self).default_get(fields)
        return_moves = return_pick['product_return_moves']
        for move in return_moves:
            if self.env['product.product'].browse(move['product_id']).\
                    product_tmpl_id.categ_id.enforce_qty_1:
                quant = self.env['stock.quant'].search(
                    [('history_ids', 'in', move['move_id'])])
                if quant and quant.lot_id:
                    move['lot_id'] = quant.lot_id.id
        return return_pick
