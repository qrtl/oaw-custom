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
    out_move_id = fields.Many2one(
        comodel_name='stock.move',
        string='Outgoing Move',
        readonly=True,
    )
    out_move_date = fields.Date(
        string='Outgoing Move Date',
        readonly=True,
    )
    in_move_id = fields.Many2one(
        comodel_name='stock.move',
        string='Incoming Move',
        readonly=True,
    )
    in_move_date = fields.Date(
        string='Incoming Move Date',
        readonly=True,
    )
    in_period_id = fields.Many2one(
        comodel_name='account.period',
        string='Period',
        readonly=True,
    )
    in_move_quant_owner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Owner',
        readonly=True,
    )
    stock_type = fields.Selection(
        [('own', 'Own Stock'),
         ('vci', 'VCI')],
        string='Stock Type',
        readonly=True,
    )


    @api.multi
    def _get_discount(self):
        for rec in self:
            if not rec.list_price or not rec.net_price:
                rec.discount = 0.0
            else:
                rec.discount = (1 - rec.net_price / rec.list_price) * 100
        return
