# -*- coding: utf-8 -*-
#    Odoo, Open Source Management Solution
#    Copyright (C) 2015-2016 Rooms For (Hong Kong) Limited T/A OSCG
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

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.one
    @api.depends('is_mto', 'partner_id')
    def _compute_order_policy(self):
        if self.is_mto:
            self.order_policy = 'line_check'
        elif self.partner_id and self.partner_id.order_policy:
            self.order_policy = self.partner_id.order_policy


    is_mto = fields.Boolean(string="Make to Order",
            readonly=True,
            states={'draft': [('readonly', False)],
                    'sent': [('readonly', False)]}
            )
    order_policy = fields.Selection(string="Create Invoice",
            selection=[('manual', 'On Demand'),
                       ('picking', 'On Delivery Order'),
                       ('prepaid', 'Before Delivery Order'),
                       ('line_check', 'Check per SO Line')],  # newly added
            required=True, readonly=True,
            states={'draft': [('readonly', False)],
                    'sent': [('readonly', False)]},
            compute='_compute_order_policy',
            help="""This field controls how invoice and delivery operations \
            are synchronized."""
            )
    is_walkin = fields.Boolean('Walk-in')



class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    @api.depends('order_id.is_mto')
    def _compute_route(self):
        model, res_id = self.env['ir.model.data'].get_object_reference('stock', 'route_warehouse0_mto')
        for line in self:
            if line.order_id.is_mto:
                line.route_id = res_id
                line.mto = True
                line.quant_id = False
                line.lot_id = False
                line.stock_owner_id = False
            else:
                line.route_id = False
                line.mto = False


    @api.model
    def _default_mto(self):
        res = self.env.context.get('is_mto',False)
        return res


    @api.model
    def _default_route(self):
        res = False
        mto = self.env.context.get('is_mto',False)
        if mto:
            model, res_id = self.env['ir.model.data'].get_object_reference('stock', 'route_warehouse0_mto')
            res = res_id
        return res



    route_id = fields.Many2one('stock.location.route',
            string="Route",
            domain=[('sale_selectable','=',True)],
            compute=_compute_route,
            default=_default_route
            )
    mto = fields.Boolean('Is MTO?',
            default=_default_mto
            )
    purchase_line_id = fields.Many2one('purchase.order.line',
            string="PO Line",
            )
    purchase_order_id = fields.Many2one('purchase.order',
            string="Purchase Order",
            related='purchase_line_id.order_id'
            )


    @api.multi
    def action_view_purchase_open(self):
        res = {}
        purchase_id = self.purchase_order_id.id
        ref = self.env['ir.model.data'].get_object_reference('sale_order_type', 'purchase_action_form_open')
        ref_id = ref and ref[1] or False
        if ref_id:
            action = self.env['ir.actions.act_window'].browse([ref_id])[0]
            res = action.read()[0]
            res['res_id'] = purchase_id
        return res
