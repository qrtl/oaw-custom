# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class SupplierStock(models.Model):
    _inherit = "supplier.stock"

    partner_loc_id_supplier = fields.Many2one(
        comodel_name='supplier.location',
        related='partner_loc_id',
        string='Partner Location',
        required=True,
    )

    @api.onchange('partner_loc_id_supplier')
    def _onchange_partner_loc_id_supplier(self):
        if self.partner_loc_id_supplier:
            self.partner_loc_id = self.partner_loc_id_supplier
            self.partner_id = self.partner_loc_id.owner_id
