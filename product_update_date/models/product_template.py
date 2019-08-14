# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    updated_date = fields.Datetime(
        compute='update_updated_date',
        store=True,
        string="Updated Date",
    )

    @api.multi
    @api.depends('list_price', 'net_price', 'qty_reserved', 'qty_local_stock',
                 'qty_overseas')
    def update_updated_date(self):
        for pt in self:
            pt.updated_date = fields.Datetime.now()

    pt_update_date = fields.Datetime(
        readonly=True,
        string='Website Update On',
    )
    pt_update_date_user_id = fields.Many2one(
        'res.users',
        readonly=True,
        string='Website Update By',
    )

    @api.multi
    def write(self, vals):
        if 'sale_hkd_ac' in vals or 'sale_hkd_ac_so' in vals \
                or 'public_categ_ids' in vals or 'retail_rmb' in vals \
                or ('partner_offer_checked' in vals and vals['partner_offer_checked']):
            vals.update({
                'pt_update_date': fields.Datetime.now(),
                'pt_update_date_user_id': self.env.user.id
            })
        return super(ProductTemplate, self).write(vals)
