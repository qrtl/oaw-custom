# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def confirm_vci_purhcase_order(self):
        for order in self:
            for order_line in order.order_line:
                if order_line.purchase_order_id and \
                        order_line.purchase_order_id.is_vci and \
                        order_line.purchase_order_id.state == 'draft':
                    order_line.purchase_order_id.signal_workflow('purchase_confirm')
