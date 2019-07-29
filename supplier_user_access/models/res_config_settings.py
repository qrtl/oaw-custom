# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_supplier_pick_partner = fields.Char(
        'Default Pick Partner For Supplier',
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        default_supplier_pick_partner = self.env['ir.config_parameter'].sudo()\
            .get_param('supplier_user_access.default_supplier_pick_partner',
                       default=False)
        res.update(default_supplier_pick_partner=default_supplier_pick_partner)
        return res

    @api.multi
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'supplier_user_access.default_supplier_pick_partner',
            self.default_supplier_pick_partner)
        super(ResConfigSettings, self).set_values()
