# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limited
# Copyright 2017 eHanse
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp



class SupplierStock(models.Model):
    _name = "supplier.stock"
    _inherit = 'mail.thread'
    _description = "Partner Stock"
    _order = "id desc"

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        required=True,
    )
    partner_loc_id = fields.Many2one(
        comodel_name='supplier.location',
        string='Partner Location',
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
        string='Internal Code',
        required=True,
    )
    product_name = fields.Char(
        string='Product Name',
        related='product_id.product_tmpl_id.name',
        store=True,
    )


    product_list_price = fields.Float(
        string='Retail HKD',
        related='product_id.list_price',
        readonly=True,
    )
    product_list_price_discount = fields.Float(
        string="Discount(%)",
        digits=dp.get_precision('Discount'),
        compute='_compute_discount',
        readonly=True
    )
    quantity = fields.Float(
        string='Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        required=True,
    )
    price_unit = fields.Float(
        string='Cost in Currency',
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
    price_unit_base = fields.Float(
        string='Unit Price (Base)',
        digits=dp.get_precision('Account'),
        compute='_compute_price_base',
        store=True,
    )
    image_small = fields.Binary(
        'Image',
        related='product_id.product_tmpl_id.image_small',
        readonly=True,
    )
    partner_note = fields.Text(
        string='Partner Note',
    )
    # Independent of current currency rate
    retail_in_currency = fields.Float(
        string='Retail in Currency',
        required=True,
        digits=dp.get_precision('Product Price'),
    )
    discount_in_curr = fields.Float(
        string='Discount in currency in %',
        required=True,
        digits=dp.get_precision('Discount'),
        compute='_discount_in_curr',
    )
    new_description = fields.Char(
        string='Reference',
        related='product_id.product_tmpl_id.name',
        readonly=True,
        store=True
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

    @api.multi
    @api.depends('price_unit','currency_id')
    def _compute_price_base(self):
        curr_obj = self.env['res.currency']
        company_curr = self.env.user.company_id.currency_id
        for rec in self:
            if rec.currency_id and rec.price_unit:
                rec.price_unit_base = curr_obj.browse(rec.currency_id.id).compute(
                rec.price_unit, company_curr)
        return

    @api.multi
    @api.depends('product_list_price', 'price_unit_base')
    def _compute_discount(self):
        for ss in self:
            if ss.product_list_price == 0.0 or ss.price_unit_base == 0.0:
                ss.product_list_price_discount = 0.0
            else:
                ss.product_list_price_discount = (1-(ss.price_unit_base/ss.product_list_price)) * 100
        return
    @api.multi
    def _discount_in_curr(self):
        for rec in self:
            if rec.retail_in_currency == 0.0 or rec.price_unit == 0.0:
                rec.discount_in_curr = 0.0
            else:
                rec.discount_in_curr = (1-(rec.price_unit/rec.retail_in_currency)) * 100
        return

# class ProductCategory(models.Model):
#
#     _inherit="product.category"
#
#     supplier_access = fields.Boolean(
#         'Available for Supplier',
#         default = False,
#         store=True,
#     )
#
#     @api.multi
#     def name_get(self, context=None):
#
#         context = self._context or {}
#         print(context)
#         if context.get('supplier_access_context',False):
#
#             res =[]
#             for cat in self:
#                 res.append(
#                     (cat.id, cat.name)
#                 )
#             return res
#         else:
#             return super(ProductCategory,self).name_get()
#
# from openerp.osv import fields, osv, orm
# from openerp import SUPERUSER_ID
#
# class ProductProduct(osv.osv):
#     _inherit = "product.product"
#     def name_get(self, cr, user, ids, context=None):
#         if context is None:
#             context = {}
#         print(context)
#         if context.get('supplier_access_context', False):
#
#             res = []
#             for product in self.browse(cr, SUPERUSER_ID, ids, context=context):
#                 res.append(
#                     (product.id, product.name)
#                 )
#             return res
#         else:
#             return super(ProductProduct, self).name_get(cr, user, ids, context=context)