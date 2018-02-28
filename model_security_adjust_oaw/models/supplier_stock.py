# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class SupplierStock(models.Model):
    _inherit = "supplier.stock"

    @api.model
    def create(self, vals):
        if not self.env.user.has_group('stock.group_stock_user'):
            vals['partner_id'] = self.env.user.partner_id.id
        return super(SupplierStock, self).create(vals)
