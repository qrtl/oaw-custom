# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class Website(models.Model):
    _inherit = "website"

    about_us = fields.Text(string="About Us")
    contact_description = fields.Text(string="Contact Information")
    empty_page_message = fields.Text(string="Empty Shop Display Message")
