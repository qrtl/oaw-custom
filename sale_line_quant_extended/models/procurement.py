# -*- coding: utf-8 -*-
# Copyright 2015-2019 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"


    @api.model
    def _update_so_line_po(self, res):
        purchase_line_id = res[self.ids[0]]
        sale_order_line = self.move_dest_id.procurement_id.sale_line_id
        self.env['sale.order.line'].browse([sale_order_line.id])[0].sudo().write({
            'purchase_line_id': purchase_line_id
        })
        self.env['purchase.order.line'].browse(
            purchase_line_id).order_id.sudo().write({
                'sale_order_customer_id': sale_order_line.order_partner_id.id
            })

    @api.multi
    def make_po(self):
        res = super(ProcurementOrder, self).make_po()
        self._update_so_line_po(res)
        return res
