# -*- coding: utf-8 -*-
#    Odoo, Open Source Management Solution
#    Copyright (C) 2015-2016 Rooms For (Hong Kong) Limited T/A OSCG
#    <https://www.odoo-asia.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from openerp import models, fields, api
from openerp.tools.translate import _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    order_type = fields.Selection(string="Order Type",
            selection=[('mto','Make to Order'),('stock','Stock')],
            required=True, readonly=True,
            states={'draft': [('readonly', False)],
                    'sent': [('readonly', False)]}
            )
    order_policy = fields.Selection(string="Create Invoice",
            selection=[('manual', 'On Demand'),
                       ('picking', 'On Delivery Order'),
                       ('prepaid', 'Before Delivery Order'),
                       ('line_check', 'Check per SO Line')],  # newly added
            required=True, readonly=True,
            states={'draft': [('readonly', False)],
                    'sent': [('readonly', False)]},
            compute='_compute_order_policy',
            help="""This field controls how invoice and delivery operations \
            are synchronized."""
            )

    @api.one
    @api.depends('order_type', 'partner_id')
    def _compute_order_policy(self):
        if self.order_type and self.order_type == 'mto':
            self.order_policy = 'line_check'
        elif self.partner_id and self.partner_id.order_policy:
            self.order_policy = self.partner_id.order_policy
