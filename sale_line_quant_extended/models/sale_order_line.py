# -*- coding: utf-8 -*-
# Copyright 2017 Rooms For (Hong Kong) Limted T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # to avoid "not enough stock" warning in case of MTO
    @api.multi
    def _check_routing(self, product, warehouse_id):
        if self._context.get('mto'):
            return True
        else:
            return super(SaleOrderLine, self)._check_routing(product,
                                                             warehouse_id)

    @api.multi
    @api.depends('order_id.is_mto')
    def _compute_route(self):
        model, res_id = self.env['ir.model.data'].get_object_reference(
            'stock', 'route_warehouse0_mto')
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
            model, res_id = self.env['ir.model.data'].get_object_reference(
                'stock', 'route_warehouse0_mto')
            res = res_id
        return res


    route_id = fields.Many2one(
        'stock.location.route',
        string="Route",
        domain=[('sale_selectable','=',True)],
        compute=_compute_route,
        default=_default_route
    )
    mto = fields.Boolean(
        'Is MTO?',
        compute=_compute_route,
        store=True,
        default=_default_mto
    )
    purchase_line_id = fields.Many2one(
        'purchase.order.line',
        string="PO Line",
        copy=False
    )
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string="Purchase Order",
        related='purchase_line_id.order_id'
    )

    @api.multi
    def action_view_purchase_open(self):
        res = {}
        purchase_id = self.purchase_order_id.id
        ref = self.env['ir.model.data'].get_object_reference(
            'sale_line_quant_extended', 'purchase_action_form_open')
        ref_id = ref and ref[1] or False
        if ref_id:
            action = self.env['ir.actions.act_window'].browse([ref_id])[0]
            res = action.read()[0]
            res['res_id'] = purchase_id
        return res
