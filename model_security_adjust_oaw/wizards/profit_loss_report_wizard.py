# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class ProfitLossReportWizard(models.TransientModel):
    _inherit = "profit.loss.report.wizard"

    @api.multi
    def action_generate_profit_loss_records(self):
        self.ensure_one()
        if self.env.user.has_group('model_security_adjust_oaw.group_supplier_fm'):
            self.env.cr.execute("DELETE FROM profit_loss_report")
            self._inject_out_invoice_data(self.from_date, self.to_date)
            self.env.cr.execute("DELETE FROM profit_loss_report WHERE "
                                "user_id IS NULL or user_id NOT IN ("
                                "   SELECT id FROM res_users WHERE partner_id "
                                "   = %d)" %
                                self.env.user.partner_id.id)
            self._update_records()
            self.env.cr.execute("UPDATE profit_loss_report SET "
                                "state = NULL,"
                                "supplier_id = NULL,"
                                "supplier_ref = NULL,"
                                "supplier_invoice_number = NULL,"
                                "supplier_payment_ref = NULL,"
                                "supplier_payment_dates = NULL,"
                                "purchase_currency_id = NULL,"
                                "purchase_currency_price = NULL,"
                                "exchange_rate = NULL,"
                                "purchase_base_price = NULL,"
                                "purchase_order_id = NULL,"
                                "purchase_invoice_id = NULL,"
                                "supplier_payment_state = NULL,"
                                "base_profit = NULL,"
                                "base_profit_percent = NULL")
            res = self.env.ref('profit_loss_report.profit_loss_report_action')
            return res.read()[0]
        return super(ProfitLossReportWizard,
                     self).action_generate_profit_loss_records()
