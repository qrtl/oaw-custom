# -*- coding: utf-8 -*-
# Copyright 2016-2017 Rooms For (Hong Kong) Limted T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.one
    @api.depends('is_mto', 'partner_id')
    def _compute_order_policy(self):
        if self.is_mto:
            self.order_policy = 'line_check'
        elif self.partner_id and self.partner_id.order_policy:
            self.order_policy = self.partner_id.order_policy


    is_mto = fields.Boolean(
        string="Make to Order",
        readonly=True,
        states={'draft': [('readonly', False)],
                'sent': [('readonly', False)]}
    )
    order_policy = fields.Selection(
        string="Create Invoice",
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
    # is_walkin = fields.Boolean('Walk-in')
    to_check = fields.Boolean(
        'To Be Checked'
    )
    # for search purpose
    seller_ids = fields.One2many(
        'Supplier',
        related='order_line.product_tmpl_id.seller_ids',
    )