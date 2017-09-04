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
    # FIXME we may deprecate this field if not needed
    sale_state = fields.Selection(
        [('open', 'Open Payment'),
         ('balance', 'Balance Payment'),
         ('done', 'Done')],
        string='Sales Status',
        readonly=True,
    )
    state = fields.Selection(
        [('purch_done', 'PO Done'),
         ('sale_done', 'SO Done'),
         ('sale_purch_done', 'SO and PO Done')],
        string='Status',
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
    purchase_order_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Purchase Order',
        readonly=True,
    )
    supplier_id = fields.Many2one(
        comodel_name='res.partner',
        string='Supplier',
        readonly=True,
    )
    supplier_ref = fields.Char(
        string='Supplier Ref.',
        readonly=True,
    )
    purchase_currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Purchase Currency',
        readonly=True,
    )
    purchase_currency_price = fields.Float(
        string="Purchase Curr. Price",
        digits=dp.get_precision('Product Price'),
        readonly=True,
    )
    exchange_rate = fields.Float(
        digits=(12, 6),
        string='FX Rate',
        readonly=True,
    )
    purchase_base_price = fields.Float(
        string='Purchase Base Price',
        digits= dp.get_precision('Account'),
        readonly = True,
    )
    purchase_invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Purchase Invoice',
        readonly=True,
    )
    supplier_invoice_number = fields.Char(
        string='Supplier Invoice No.',
        readonly=True,
    )
    base_profit = fields.Float(
        string='Base Profit',
        readonly=True,
    )
    base_profit_percent = fields.Float(
        string='Profit %',
        digits=dp.get_precision('Discount'),
        readonly=True,
    )
    customer_payment_ids = fields.Many2many(
        string='Customer Payment',
        comodel_name='account.move.line',
        related='invoice_id.payment_ids',
        readonly=True,
    )
    customer_payment_dates = fields.Char(
        string='Payment Date',
        readonly=True,
    )
    customer_payment_ref = fields.Char(
        string='Payment Ref.',
        readonly=True,
    )
    supplier_payment_ids = fields.Many2many(
        string='Supplier Payment',
        comodel_name='account.move.line',
        related='purchase_invoice_id.payment_ids',
        readonly=True,
    )
    supplier_payment_dates = fields.Char(
        string='Payment Date',
        readonly=True,
    )
    supplier_payment_ref = fields.Char(
        string='Payment Ref.',
        readonly=True,
    )
    supplier_payment_ref = fields.Char(
        string='Payment Ref.',
        readonly=True,
    )
    supplier_payment_state = fields.Selection(
        [('to_pay', 'To Be Paid'),
         ('done', 'Done')],
        string='Supplier Payment Status',
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
