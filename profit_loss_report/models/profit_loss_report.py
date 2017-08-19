# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields


class ProfitLossReport(models.TransientModel):
    _name = 'profit.loss.report'

    categ_id = fields.Many2one(
        comodel_name='product.category',
        string='Brand'
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Reference',
    )
