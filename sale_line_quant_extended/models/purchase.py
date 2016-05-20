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

from openerp import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"


    @api.multi
    def action_picking_create(self):
        for order in self:
            picking_vals = {
                'picking_type_id': order.picking_type_id.id,
                'partner_id': order.partner_id.id,
                'date': order.date_order,
                'origin': order.name,
                'is_mto': order.is_mto  # oscg added
            }
            picking_id = self.env['stock.picking'].create(picking_vals).id
            self._create_stock_moves(order, order.order_line, picking_id)
        return picking_id



class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"


    @api.one
    @api.depends('move_ids.state')
    def _get_move_state(self):
        if all(m.state == 'cancel' for m in self.move_ids):
            self.move_state = 'cancel'
        else:
            state = ''
            for m in self.move_ids:
                if m.state == 'cancel':
                    pass
                elif state == '':
                    state = m.state
                elif state != m.state:
                    state = 'multi'
            self.move_state = state


    move_state = fields.Selection(
        [('draft', 'New'),
         ('cancel', 'Cancelled'),
         ('confirmed', 'Waiting Availability'),
         ('assigned', 'Available'),
         ('done', 'Done'),
         ('multi', '(Multiple Statuses)'),
        ],
        compute=_get_move_state,
        store=True,
        readonly=True,
        copy=False,
        string="Move State"
    )
