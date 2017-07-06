# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ProductProduct(models.Model):
    _inherit = "product.product"


    @api.multi
    def update_updated_date(self):
        for p in self:
            p.product_tmpl_id.updated_date = fields.Datetime.now()
