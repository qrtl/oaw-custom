# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        for order in self:
            if order.subconsigned and order.state not in 'cancel':
                order.order_line.filtered(
                    lambda l: l.product_id.categ_id.enforce_qty_1).create_update_consignment_partner_stock()
            else:
                order.order_line.unlink_consignment_partner_stock()
        return res

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        for order in res:
            if order.subconsigned:
                order.order_line.filtered(
                    lambda l: l.product_id.categ_id.enforce_qty_1).create_update_consignment_partner_stock()
        return res
