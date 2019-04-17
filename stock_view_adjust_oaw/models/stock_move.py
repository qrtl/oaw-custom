# Copyright 2019 Quartile Limited
# Copyright 2017 eHanse
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class StockMove(models.Model):
    _inherit = "stock.move"

    image_small = fields.Binary(
        'Image',
        related='product_id.product_tmpl_id.image_small',
        readonly=True,
    )
    line_sequence = fields.Integer(
        string="Sequence",
        readonly=True,
    )
