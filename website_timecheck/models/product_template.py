# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    partner_stock_special_offer = fields.Datetime(
        string="Special Offer",
    )
    partner_stock_new_arrival = fields.Datetime(
        string="New Arrival",
    )
    partner_stock_retail_currency_price = fields.Float(
        string='Retail in Currency',
        digits=dp.get_precision('Product Price'),
    )
    partner_stock_retail_currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
    )
