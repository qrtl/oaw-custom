# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    about_us = fields.Text(
        string="About Us", related="website_id.about_us", readonly=False
    )
    contact_description = fields.Text(
        string="Contact Information",
        related="website_id.contact_description",
        readonly=False,
    )
    empty_page_message = fields.Text(
        string="Empty Shop Display Message",
        related="website_id.empty_page_message",
        readonly=False,
    )
