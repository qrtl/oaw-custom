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
        for p in self:
            p.updated_date = fields.Datetime.now()
            ss_recs = self.env['supplier.stock'].search(
                [('product_id', '=', p.id)])
            if ss_recs:
                for rec in ss_recs:
                    rec.write({'updated_date': p.updated_date})
