# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class SupplierStock(models.Model):
    _inherit = "supplier.stock"

    updated_date = fields.Datetime(
        default=fields.Datetime.now(),
        string="Updated Date",
    )


    @api.multi
    def write(self, vals):
        if not vals.get('updated_date'):
            vals['updated_date'] = fields.Datetime.now()
        return super(SupplierStock, self).write(vals)
