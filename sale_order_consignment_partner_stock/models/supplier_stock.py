# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class SupplierStock(models.Model):
    _inherit = 'supplier.stock'

    order_line_id = fields.Many2one(
        'sale.order.line',
        string='Order Reference',
        ondelete='cascade',
        readonly=True,
    )
    order_id = fields.Many2one(
        related='order_line_id.order_id',
        string='Order Reference',
        readonly=True,
    )
