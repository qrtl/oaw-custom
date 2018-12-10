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
        help="Quantity on hand plus incoming quantity from stock moves that"
             "are 'Available' ('assigned') state.",
        copy=False,
    )
    local_stock_not_reserved = fields.Integer(
        string="Local Stock",
        compute="_get_local_stock_not_reserved",
        store=True,
        readonly=True,
    )
    qty_reserved = fields.Integer(
        string="Quantity Reserved",
        readonly=True,
        copy=False,
    )
    qty_overseas = fields.Integer(
        string="Quantity Overseas",
        readonly=True,
        copy=False,
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
    sale_hkd_ab = fields.Integer(
        string="Stock Sale HKD AB",
        digits=dp.get_precision('Product Price'),
        store=True
    )
    sale_hkd_aa_so = fields.Integer(
        string="Stock Sale HKD AA Special Offer",
        digits=dp.get_precision('Product Price'),
        store=True
    )
    sale_hkd_ac = fields.Integer(
        string="Stock Sale HKD AB",
        digits=dp.get_precision('Product Price'),
        store=True
    )
    sale_hkd_ac_so = fields.Integer(
        string="Stock Sale HKD AC Special Offer",
        digits=dp.get_precision('Product Price'),
        store=True
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
    discount_aa_so = fields.Float(
        string="Discount (%)",
        digits=dp.get_precision('Discount'),
        compute='_get_discount_aa_so',
        readonly=True,
    )
    discount_ac = fields.Float(
        string="Discount (%)",
        digits=dp.get_precision('Discount'),
        compute='_get_discount_ac',
        readonly=True,
    )
    discount_ac_so = fields.Float(
        string="Discount (%)",
        digits=dp.get_precision('Discount'),
        compute='_get_discount_ac_so',
        readonly=True,
    )
    net_price_cny = fields.Float(
        string='Sale RMB',
        compute='_get_net_price_cny',
        digits=dp.get_precision('Product Price')
    )
    sale_hkd_aa_so_cn = fields.Integer(
        string='Sale AB RMB',
        compute='_get_net_price_cny',
        digits=dp.get_precision('Product Price')
    )
    sale_hkd_ac_cn = fields.Integer(
        string='Sale AC RMB',
        compute='_get_net_price_cny',
        digits=dp.get_precision('Product Price')
    )
    sale_hkd_ac_so_cn = fields.Integer(
        string='Sale AB RMB',
        compute='_get_net_price_cny',
        digits=dp.get_precision('Product Price')
    )


    partner_stock_last_modified = fields.Datetime(
        string="Last Modified",
        readonly=True,
        store=True,
    )

    @api.multi
    def _get_net_price_cny(self):
        cny_rec = self.env['res.currency'].search([('name','=','CNY')])[0]
        if cny_rec:
            for pt in self:
                pt.net_price_cny = pt.net_price * cny_rec.rate_silent
                pt.sale_hkd_aa_so_cn = pt.sale_hkd_aa_so * cny_rec.rate_silent
                pt.sale_hkd_ac_cn = pt.sale_hkd_ac * cny_rec.rate_silent
                pt.sale_hkd_ac_so_cn = pt.sale_hkd_aa_so * cny_rec.rate_silent

    @api.multi
    @api.depends('list_price', 'net_price')
    def _get_discount(self):
        for pt in self:
            if not pt.list_price or not pt.net_price:
                pt.discount = 0.0
            else:
                pt.discount = (1 - pt.net_price / pt.list_price) * 100
        return

    @api.multi
    @api.depends('list_price', 'sale_hkd_aa_so')
    def _get_discount_aa_so(self):
        for pt in self:
            if not pt.list_price or not pt.sale_hkd_aa_so:
                pt.discount_aa_so = 0.0
            else:
                pt.discount_aa_so = (1 - pt.sale_hkd_aa_so / pt.list_price) * 100
        return
    @api.multi
    @api.depends('list_price', 'sale_hkd_ac')
    def _get_discount_ac(self):
        for pt in self:
            if not pt.list_price or not pt.sale_hkd_ac:
                pt.discount_ac = 0.0
            else:
                pt.discount_ac = (1 - pt.sale_hkd_ac / pt.list_price) * 100
        return
    @api.multi
    @api.depends('list_price', 'sale_hkd_ac_so')
    def _get_discount_ac_so(self):
        for pt in self:
            if not pt.list_price or not pt.sale_hkd_ac_so:
                pt.discount_ac_so = 0.0
            else:
                pt.discount_ac_so = (1 - pt.sale_hkd_ac_so / pt.list_price) * 100
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
    @api.depends('qty_local_stock')
    def _get_local_stock(self):
        for pt in self:
            if pt.qty_local_stock > 0:
                pt.local_stock = 'Yes'
            else:
                pt.local_stock = 'No'
    @api.multi
    @api.depends('qty_local_stock', 'qty_reserved')
    def _get_local_stock_not_reserved(self):
        for pt in self:
            pt.local_stock_not_reserved = pt.qty_local_stock - pt.qty_reserved
    @api.multi
    @api.depends('qty_overseas')
    def _get_overseas_stock(self):
        for pt in self:
            if pt.qty_overseas > 0:
                pt.overseas_stock = 'Yes'
            else:
                pt.overseas_stock = 'No'
