# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class WebsiteConfigSettings(models.Model):
    _inherit = 'website.config.settings'

    sale_user_id = fields.Many2one(
        related='website_id.sale_user_id',
        string='Online Salesperson',
    )
