# Copyright 2020 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SupplierStock(models.Model):
    _inherit = "supplier.stock"

    website_published = fields.Boolean(
        'Visible in Portal / Website',
        copy=False,
    )
    readonly_record = fields.Boolean(
        'Readonly Record',
        copy=False,
        default=False,
    )
