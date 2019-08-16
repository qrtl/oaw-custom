# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    online_quotation = fields.Boolean(
        string="Is Online Quotation?",
        compute="_compute_online_quotation",
    )

    @api.multi
    def _compute_online_quotation(self):
        online_salesperson = self.env['website'].get_current_website(
        ).sale_user_id
        for order in self:
            order.online_quotation = True if order.state != 'cancel' and \
                order.user_id == online_salesperson else False

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        for order in self:
            order._update_order_line_sequence()
        return res

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        for order in res:
            order._update_order_line_sequence()
        return res

    def _update_order_line_sequence(self):
        order_lines = sorted(self.order_line, key=lambda r: (
            r.sequence, r.id))
        sequence = 1
        for order_line in order_lines:
            order_line.line_sequence = sequence
            sequence += 1
