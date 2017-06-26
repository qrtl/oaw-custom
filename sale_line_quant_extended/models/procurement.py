# -*- coding: utf-8 -*-
# Copyright 2015-2017 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp import SUPERUSER_ID


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"


    @api.model
    def _update_so_line(self, res):
        purchase_line_id = res[self.ids[0]]
        sale_line_id = self.move_dest_id.procurement_id.sale_line_id.id
        self.env['sale.order.line'].browse([sale_line_id])[0].sudo(SUPERUSER_ID).write({'purchase_line_id': purchase_line_id})


    @api.multi
    def make_po(self):
        res = super(ProcurementOrder, self).make_po()
        self._update_so_line(res)
        return res
