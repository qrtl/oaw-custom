# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class SupplierStock(models.Model):
    _inherit = "supplier.stock"

    partner_id = fields.Many2one(
        default=lambda self: self.env.user.partner_id
    )
    internal_code = fields.Char(
        "Internal Code",
        related='product_id.product_tmpl_id.default_code',
        readonly=True,
        store=True,
    )
    prod_cat_selection = fields.Many2one(
        comodel_name='product.category',
        string='Brand',
        required=True,
    )
    #For form view image
    image_medium = fields.Binary(
        'Image',
        related='product_id.product_tmpl_id.image_medium',
        readonly=True,
    )
    owners_duplicates = fields.Boolean(
        string='Your duplicates',
        store=True,
    )
    mto_amount = fields.Integer(
        string = "Ordered",
        compute = '_get_ordered_amount'
    )

    # Overwriting display_name's method for Supplier Access User
    @api.multi
    def name_get(self, *args, **kwargs):
        result = []
        for rec in self:
            result.append(
                (rec.id, rec.product_id.name)
            )
        return result

    # Takes care of the product selection in Supplier Access views
    @api.onchange('prod_cat_selection')
    def on_change_category(self):
        ids = []
        if self.product_id.categ_id != self.prod_cat_selection:
            if self.prod_cat_selection and not self.product_id:
                products = self.env['product.product'].search([
                    ('categ_id', '=', self.prod_cat_selection.id)
                ])
                ids.append(('id', 'in', products.ids))
                return {
                    'domain': {'product_id': ids}
                }
            if self.prod_cat_selection and self.product_id:
                self.product_id = False
                products = self.env['product.product'].search([
                    ('categ_id', '=', self.prod_cat_selection.id)
                ])
                ids.append(('id', 'in', products.ids))
                return {
                    'domain': {'product_id': ids}
                }
        if not self.prod_cat_selection:
            self.product_id = False

    @api.onchange('product_id')
    def on_change_product(self):
        if self.product_id and not self.prod_cat_selection:
            the_category = self.product_id.categ_id
            self.prod_cat_selection = the_category

    @api.onchange('partner_loc_id')
    def _onchange_partner_loc_id(self):
        if self.partner_loc_id:
            self.partner_id = self.partner_loc_id.owner_id

    @api.multi
    def _get_owners_duplicates(self):
        for ps in self:
            # Duplicates of the supplier accessing his entries
            owners_duplicates = self.sudo().search(
                [('product_id', '=', ps.product_id.id),
                 ('partner_id', '=', ps.partner_id.id),
                 ], order='price_unit_base ASC'
            )
            if owners_duplicates:
                if len(owners_duplicates) >= 2:
                    owners_duplicates.sudo().write({'owners_duplicates': True})
                else:
                    owners_duplicates.sudo().write({'owners_duplicates': False})
    @api.multi
    def write(self, vals):
        for ps in self:
            if 'quantity' in vals:
                ps._get_owners_duplicates()
        res = super(SupplierStock, self).write(vals)
        for ps in self:
            if self.env.user.has_group('model_security_adjust_oaw.group_supplier'):
                server_actions = self.env['base.action.rule'].sudo().search([
                    ('model', '=', 'supplier.stock'),
                    ('kind', 'in', ('on_write', 'on_create_or_write')),
                    ('active', '=', True)
                ], order='sequence')
                for action in server_actions:
                    action.sudo()._process(action, [ps.id])
        return res

    @api.model
    def create(self, vals):
        res = super(SupplierStock, self).create(vals)
        res._get_owners_duplicates()
        if self.env.user.has_group('model_security_adjust_oaw.group_supplier'):
            server_actions = self.env['base.action.rule'].sudo().search([
                ('model', '=', 'supplier.stock'),
                ('kind', 'in', ('on_create', 'on_create_or_write')),
                ('active', '=', True)
            ], order='sequence')
            for action in server_actions:
                action.sudo()._process(action, [res.id])
        return res
    @api.multi
    def _get_ordered_amount(self):
        for ss in self:
            sol= self.env['sale.order.line'].sudo().search([
                    ('is_mto', '=', True),
                    ('state', 'in', ('draft', 'sent')),
                    ('product_id', '=', ss.product_id.id)
                ])

            i = 0
            for line in sol:
                if line.order_id.supplier_id == self.env.user.partner_id:
                    if line.qty > 1:
                        i = i + line.qty
                    else:
                        i += 1
            ss.mto_amount = i
