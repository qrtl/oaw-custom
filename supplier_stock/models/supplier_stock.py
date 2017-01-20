# -*- coding: utf-8 -*-
# Copyright 2017 Rooms For (Hong Kong) Limted T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class SupplierStock(models.Model):
    _name = "supplier.stock"
    _description = "Supplier Stock"
    _order = "id desc"

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Supplier',
        required=True,
    )
    partner_loc_id = fields.Many2one(
        comodel_name='supplier.location',
        string='Supplier Location',
        required=True,
    )
    supplier_lead_time = fields.Integer(
        string='Lead Time',
        related='partner_loc_id.supplier_lead_time',
        readonly=True,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        required=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
    )
    quantity = fields.Float(
        string='Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        required=True,
    )
    price_unit = fields.Float(
        string='Unit Price',
        required=True,
        digits=dp.get_precision('Product Price'),
    )
    price_subtotal = fields.Float(
        string='Amount',
        digits=dp.get_precision('Account'),
        store=True,
        readonly=True,
        compute='_compute_price'
    )


    @api.one
    @api.depends('price_unit', 'quantity', 'currency_id')
    def _compute_price(self):
        self.price_subtotal = self.price_unit * self.quantity
        if self.currency_id:
            self.price_subtotal = self.currency_id.round(self.price_subtotal)

    @api.one
    @api.onchange('partner_loc_id')
    def _onchange_partner_loc_id(self):
        if not self.partner_loc_id:
            self.currency_id = False
        else:
            self.currency_id = self.partner_loc_id.currency_id
