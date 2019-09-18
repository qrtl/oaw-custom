# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class StockLocation(models.Model):
    _inherit = 'stock.location'

    repair_location = fields.Boolean(
        string='Is a Repair Location?',
    )
