# -*- coding: utf-8 -*-
# Copyright 2015-2017 Rooms For (Hong Kong) Limted T/A OSCG
# Copyright 2017 eHanse
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class StockMove(models.Model):
    _inherit = "stock.move"
    image_small = fields.Binary(
        'Image',
        related='product_id.product_tmpl_id.image_small',
    )
