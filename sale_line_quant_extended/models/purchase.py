# -*- coding: utf-8 -*-
# Copyright 2015-2017 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _, SUPERUSER_ID


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
        if self.move_ids:
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
        else:
            self.move_state = 'na'


    move_state = fields.Selection(
        [('draft', 'New'),
         ('cancel', 'Cancelled'),
         ('confirmed', 'Waiting Availability'),
         ('assigned', 'Available'),
         ('done', 'Done'),
         ('na', '(N/A)'),
         ('multi', '(Multiple Statuses)'),
        ],
        compute=_get_move_state,
        store=True,
        readonly=True,
        copy=False,
        string="Move State"
    )


    def init(self, cr):
        line_ids = self.search(cr, SUPERUSER_ID, [('move_state','=',False)])
        lines = self.browse(cr, SUPERUSER_ID, line_ids)
        for line in lines:
            if line.move_ids:
                if all(m.state == 'cancel' for m in line.move_ids):
                    line.move_state = 'cancel'
                else:
                    state = ''
                    for m in line.move_ids:
                        if m.state == 'cancel':
                            pass
                        elif state == '':
                            state = m.state
                        elif state != m.state:
                            state = 'multi'
                    line.move_state = state
            else:
                line.move_state = 'na'
