# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class SupplierStock(models.Model):
    _inherit = "supplier.stock"

    hk_location = fields.Boolean(
        related='partner_loc_id.hk_location'
    )

    @api.multi
    def _update_prod_tmpl_qty(self):
        for ss in self:
            ss.product_id._update_prod_tmpl_qty()
