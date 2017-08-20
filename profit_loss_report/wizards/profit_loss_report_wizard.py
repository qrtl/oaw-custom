# -*- coding: utf-8 -*-
# Copyright 2016-2017 Rooms For (Hong Kong) Limited T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import api, models, fields


class ProfitLossReportWizard(models.TransientModel):
    _name = "profit.loss.report.wizard"
    _description = 'Profit & Loss Report Wizard'

    threshold_date = fields.Date(
        required=True,
        string='Threshold Date',
        default=fields.Date.to_string(
            datetime.now() - relativedelta(days=90)),
    )


    def _inject_data(self, threshold_date):
        query = """
        INSERT INTO
            profit_loss_report
            (
            create_uid,
            create_date,
            product_id,
            categ_id,
            categ_name,
            lot_id,
            date_order,
            user_id,
            sale_order_id,
            invoice_id,
            list_price,
            net_price,
            partner_id,
            partner_ref,
            sale_order_note
            )
        SELECT
            %s AS create_uid,
            NOW() AS create_date,
            pp.id,
            pc.id,
            pc.name,
            ail.lot_id,
            so.date_order,
            ai.user_id,
            so.id,
            ai.id,
            pt.list_price,
            pt.net_price,
            so.partner_id,
            rp.ref,
            so.note
        FROM
            account_invoice_line ail
        JOIN
            account_invoice ai ON ail.invoice_id = ai.id
        JOIN
            product_product pp ON ail.product_id = pp.id
        JOIN
            product_template pt ON pp.product_tmpl_id = pt.id
        JOIN
            product_category pc ON pt.categ_id = pc.id
        JOIN
            res_partner rp ON ai.partner_id = rp.id
        LEFT JOIN
            sale_order so ON ail.so_id = so.id
        WHERE
            ai.type = 'out_invoice' AND
            ai.state in ('open', 'paid') AND
            ai.date_invoice >= %s
        """
        params = (
            self.env.uid,
            threshold_date
        )
        self.env.cr.execute(query, params)


    @api.multi
    def action_generate_profit_loss_records(self):
        self.ensure_one()
        self.env.cr.execute("""
            DELETE FROM profit_loss_report
        """)
        self._inject_data(self.threshold_date)
        return {'type': 'ir.actions.act_window_close'}
