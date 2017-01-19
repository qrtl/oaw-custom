# -*- coding: utf-8 -*-
# Copyright 2017 Rooms For (Hong Kong) Limted T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # @api.model
    # def _get_qty_overseas(self, p_id):
    #     res = 0.0
    #     supp_stock_obj = self.env['supplier.stock']
    #     records = supp_stock_obj.search([
    #         ('product_id', '=', p_id),
    #     ])
    #     for rec in records:
    #         res += rec.quantity
    #     return res
    #

    # this field is added due to kanban view limitation
    list_price_integer = fields.Integer(
        string="Sale Price",
        compute="_get_list_price_integer",
        store=True,
    )
    qty_local_atp = fields.Integer(
        string="Quantity Local ATP",
    )
    qty_reserved = fields.Integer(
        string="Quantity Reserved",
    )
    qty_overseas = fields.Integer(
        string="Quantity Overseas",
        # compute="_get_qty_info",
    )
    last_in_date = fields.Datetime(
        string="Last Incoming Date",
    )
    local_atp = fields.Char(
        string="Local ATP",
    )


    @api.multi
    @api.depends('list_price')
    def _get_list_price_integer(self):
        for prod in self:
            prod.list_price_integer = int(prod.list_price)
