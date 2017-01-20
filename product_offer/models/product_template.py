# -*- coding: utf-8 -*-
# Copyright 2017 Rooms For (Hong Kong) Limted T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # this field is added due to kanban view limitation
    # i.e. decimal place values cannot be eliminated by view adjustment
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
    )
    last_in_date = fields.Datetime(
        string="Last Incoming Date",
    )
    local_stock = fields.Char(
        string="Local Stock",
        compute="_get_local_stock",
        store=True,
    )
    overseas_stock = fields.Char(
        string="Overseas Stock",
        compute="_get_overseas_stock",
        store=True,
    )


    @api.multi
    @api.depends('list_price')
    def _get_list_price_integer(self):
        for pt in self:
            pt.list_price_integer = int(pt.list_price)

    @api.multi
    @api.depends('qty_local_atp', 'qty_reserved')
    def _get_local_stock(self):
        for pt in self:
            local_stock_qty = pt.qty_local_atp - pt.qty_reserved
            if local_stock_qty > 0:
                pt.local_stock = 'Yes'
            else:
                pt.local_stock = '/'

    @api.multi
    @api.depends('qty_overseas')
    def _get_overseas_stock(self):
        for pt in self:
            if pt.qty_overseas > 0:
                pt.overseas_stock = 'Yes'
            else:
                pt.overseas_stock = '/'
