# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class Website(models.Model):
    _inherit = 'website'

    about_us = fields.Text(
        string='About Us',
    )
    contact_description = fields.Text(
        string='Contact Information',
    )
