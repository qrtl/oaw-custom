# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limited
# Copyright 2017 eHanse
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields


class SupplierStockRevaluationWizard(models.TransientModel):
    _name = "supplier.stock.revaluation.wizard"
    _description = 'Supplier Stock Revaluation Wizard'

    @api.multi
    def action_supplier_stock_revaluation(self):
        self.ensure_one()
        if self.env.context.get('active_ids', False):
            product_ids = self.env.context.get('active_ids')
        else:
            product_ids = []
        self.env['supplier.stock'].revaluate_supplier_stock(product_ids)
        return {'type': 'ir.actions.act_window_close'}
