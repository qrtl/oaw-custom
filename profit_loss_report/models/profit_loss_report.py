# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class ProfitLossReport(models.TransientModel):
    _name = 'profit.loss.report'

    categ_id = fields.Many2one(
        comodel_name='product.category',
        string='Product Category',
        readonly=True,
    )
    categ_name = fields.Char(
        string='Brand',
        readonly=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Referece',
        readonly=True,
    )
    lot_id = fields.Many2one(
        comodel_name='stock.production.lot',
        string='Case No.',
        readonly=True,
    )
    date_order = fields.Date(
        string='Date Registered',
        readonly=True,
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Salesperson',
        readonly=True,
    )
    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Quotation',
        readonly=True,
    )
    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice',
        readonly=True,
    )
    list_price = fields.Float(
        string='HK Retail',
        digits=dp.get_precision('Product Price'),
        readonly=True,
    )
    discount = fields.Float(
        string="Discount (%)",
        digits=dp.get_precision('Discount'),
        compute='_get_discount',
        readonly=True,
    )
    net_price = fields.Float(
        string="Net Price",
        digits=dp.get_precision('Product Price'),
        readonly=True,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        readonly=True,
    )
    partner_ref = fields.Char(
        string='Customer Ref.',
        readonly=True,
    )
    sale_order_note = fields.Text(
        string='Quotation Notes',
        readonly=True,
    )


    @api.multi
    @api.depends('list_price', 'net_price')
    def _get_discount(self):
        for pt in self:
            if not pt.list_price or not pt.net_price:
                pt.discount = 0.0
            else:
                pt.discount = (1 - pt.net_price / pt.list_price) * 100
        return
