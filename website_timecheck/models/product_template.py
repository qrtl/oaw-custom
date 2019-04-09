# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
from openerp import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    stock_new_arrival = fields.Datetime(
        string='New Arrival',
    )
    is_new_arrival = fields.Boolean(
        string='New Arrival',
        compute='_get_is_new_arrival',
    )

    @api.multi
    def _get_is_new_arrival(self):
        for product in self:
            now = (datetime.datetime.now() + datetime.timedelta(
                days=-7)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            product.is_new_arrival = True if \
                product.stock_new_arrival and \
                product.stock_new_arrival >= now else False

    @api.multi
    def write(self, vals):
        if 'qty_local_stock' in vals or 'qty_overseas' in vals or \
                'qty_reserved' in vals:
            for product in self:
                qty_local_stock = vals.get('qty_local_stock',
                                           product.qty_local_stock)
                qty_overseas = vals.get('qty_overseas', product.qty_overseas)
                qty_reserved = vals.get('qty_reserved', product.qty_reserved)
                if product.qty_overseas < qty_overseas or \
                        product.qty_local_stock < qty_local_stock and \
                        qty_local_stock > qty_reserved:
                    product.sudo().write({
                        'stock_new_arrival': fields.Datetime.now()
                    })
                elif qty_local_stock == qty_reserved:
                    product.sudo().write({
                        'stock_new_arrival': False
                    })
        return super(ProductTemplate, self).write(vals)

    @api.multi
    def update_public_category(self):
        for product in self:
            if product.categ_id and not product.public_categ_ids:
                public_categ_ids = self.env['product.public.category'].search([
                    ('name', '=', product.categ_id.name)
                ])
                product.public_categ_ids = public_categ_ids
