# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class ExportProductImage(models.TransientModel):
    _name = "export.product.image"

    image = fields.Binary(
        string="Image Download",
        readonly=True,
    )
    name = fields.Char(
        string='Exported Image',
    )

    @api.multi
    def download_image(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/saveas?model=export.product.image&field'
                   '=image&id=%d&filename_field=%s' % (self.id, 'name'),
            'target': 'self'
        }
