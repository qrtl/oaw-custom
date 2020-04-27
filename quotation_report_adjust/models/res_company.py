# Copyright 2020 Timeware Limited & Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class Company(models.Model):
    _inherit = "res.company"

    logo2 = fields.Binary('Another Logo',  store=True)
    