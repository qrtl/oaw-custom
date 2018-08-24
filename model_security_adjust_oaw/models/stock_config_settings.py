# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class StockConfigSettings(models.TransientModel):
    _inherit = 'stock.config.settings'

    default_supplier_pick_partner = fields.Char(
        'Default Pick Partner For Supplier',
    )

    @api.model
    def get_default_supplier_pick_partner(self, fields):
        param = self.env['ir.config_parameter']
        return {
            'default_supplier_pick_partner': param.get_param(
                'default_supplier_pick_partner'),
        }

    @api.multi
    def set_default_supplier_pick_partner(self):
        for config in self:
            param = self.env['ir.config_parameter']
            param.set_param('default_supplier_pick_partner',
                            config.default_supplier_pick_partner or '')
