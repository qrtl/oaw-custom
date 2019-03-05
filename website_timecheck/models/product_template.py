# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    partner_stock_special_offer = fields.Datetime(
        string='Special Offer',
    )
    partner_stock_new_arrival = fields.Datetime(
        string='New Arrival',
    )
    partner_stock_retail_currency_price = fields.Float(
        string='Retail in Currency',
        digits=dp.get_precision('Product Price'),
    )
    partner_stock_retail_currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
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
            print product.partner_stock_new_arrival
            print now
            product.is_new_arrival = True if \
                product.partner_stock_new_arrival and \
                product.partner_stock_new_arrival >= now else False
