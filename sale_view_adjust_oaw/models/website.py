# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class Website(models.Model):
    _inherit = 'website'

    user_id = fields.Many2one(
        'res.users',
        string='Online Salesperson',
    )
