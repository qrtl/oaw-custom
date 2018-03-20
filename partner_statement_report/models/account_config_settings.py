# -*- coding: utf-8 -*-
# Copyright 2017-2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    initial_balance_mode = fields.Selection(
        [('initial_balance', 'Compute Balance'),
         ('opening_balance', 'Opening Balance')],
        'Initial Balance Mode',
    )

    @api.model
    def get_default_balance_mode(self, fields):
        param = self.env['ir.config_parameter']
        return {
            'initial_balance_mode': param.get_param('initial_balance_mode'),
        }

    @api.multi
    def set_initial_balance_mode(self):
        for config in self:
            param = self.env['ir.config_parameter']
            param.set_param('initial_balance_mode', config.initial_balance_mode)
