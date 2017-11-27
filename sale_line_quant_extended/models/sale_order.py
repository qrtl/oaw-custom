# -*- coding: utf-8 -*-
# Copyright 2015-2017 Quartile Limted
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
    # For communication with warehouse group
    to_check = fields.Boolean(
        'To Be Checked'
    )

    # Field for communication with Delivery Group
    open_issue = fields.Boolean(
        'Open Issue'
    )

    # Field for communication with Accounting
    checked = fields.Boolean(
        'Checked'
    )

    # for search purpose
    seller_ids = fields.One2many(
        comodel_name='product.supplierinfo',
        related='order_line.product_tmpl_id.seller_ids',
        string='Supplier',
    )

    @api.multi
    def action_orders_2(self):
        view_id = self.env.ref('sale.view_order_form').id
        context = {}
        return {
            'name':'Sales Order',
            'view_mode':'form',
            'view_type': 'form',
            'res_model':'sale.order',
            'view_id':view_id,
            'type':'ir.actions.act_window',
            'res_id':self.id,
            'context':context,
        }