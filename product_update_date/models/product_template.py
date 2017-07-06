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
