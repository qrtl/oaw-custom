# -*- coding: utf-8 -*-
# Copyright 2017 Rooms For (Hong Kong) Limted T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # this field is added due to kanban view limitation
    # i.e. decimal place values cannot be eliminated by view adjustment
    list_price_integer = fields.Integer(
        string="Sale Price",
        compute="_get_list_price_integer",
        store=True,
        readonly=True,
    )
    qty_local_stock = fields.Integer(
        string="Quantity Local Stock",
        readonly=True,
    )
    qty_reserved = fields.Integer(
        string="Quantity Reserved",
        readonly=True,
    )
    qty_overseas = fields.Integer(
        string="Quantity Overseas",
        readonly=True,
    )
    last_in_date = fields.Datetime(
        string="Last Incoming Date",
        readonly=True,
    )
    local_stock = fields.Char(
        string="Local Stock",
        compute="_get_local_stock",
        store=True,
        readonly=True,
    )
    qty_local_atp = fields.Integer(
        string="Quantity Local ATP",
        compute="_get_local_stock",
        store=True,
        readonly=True,
    )
    overseas_stock = fields.Char(
        string="Overseas Stock",
        compute="_get_overseas_stock",
        store=True,
        readonly=True,
    )
    supplier_id = fields.Many2one(  # for search purpose
        comodel_name="res.partner",
        string='Supplier',
        related='seller_ids.name',
        store=True,
    )
    net_price = fields.Float(
        string="Net Price",
        digits=dp.get_precision('Product Price'),
    )
    net_price_integer = fields.Integer(  # for kanban presentation
        string="Net Price",
        compute="_get_net_price_integer",
        store=True,
        readonly=True,
    )
    discount = fields.Float(
        string="Discount (%)",
        digits=dp.get_precision('Discount'),
        compute='_get_discount',
        readonly=True,
    )


    @api.multi
    @api.depends('list_price', 'net_price')
    def _get_discount(self):
        for pt in self:
            if not pt.list_price:
                pt.discount = 0.0
            else:
                pt.discount = (1 - pt.net_price / pt.list_price) * 100
        return

    @api.multi
    @api.depends('list_price')
    def _get_list_price_integer(self):
        for pt in self:
            pt.list_price_integer = int(pt.list_price)

    @api.multi
    @api.depends('net_price')
    def _get_net_price_integer(self):
        for pt in self:
            pt.net_price_integer = int(pt.net_price)

    @api.multi
    @api.depends('qty_local_stock', 'qty_reserved')
    def _get_local_stock(self):
        for pt in self:
            local_atp_qty = pt.qty_local_stock - pt.qty_reserved
            if local_atp_qty > 0:
                pt.local_stock = 'Yes'
            else:
                pt.local_stock = 'No'
            pt.qty_local_atp = local_atp_qty

    @api.multi
    @api.depends('qty_overseas')
    def _get_overseas_stock(self):
        for pt in self:
            if pt.qty_overseas > 0:
                pt.overseas_stock = 'Yes'
            else:
                pt.overseas_stock = 'No'
