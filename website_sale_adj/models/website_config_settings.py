# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class WebsiteConfigSettings(models.Model):
    _inherit = 'website.config.settings'

    about_us = fields.Text(
        related='website_id.about_us',
        string='About Us',
    )
    contact_description = fields.Text(
        related='website_id.contact_description',
        string='Contact Information',
    )
