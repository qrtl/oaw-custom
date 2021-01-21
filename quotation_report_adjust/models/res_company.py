# Copyright 2020 Timeware Limited
# Copyright 2021 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResComopany(models.Model):
    _inherit = "res.company"

    alternative_logo = fields.Binary("Alternative Logo")
