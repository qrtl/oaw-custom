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


    @api.multi
    def action_generate_profit_loss_records(self):
        self.ensure_one()
        # model = self.env['offer.report']
        # report = model.create(
        #     {'threshold_date': self.threshold_date}
        # )
        return {'type': 'ir.actions.act_window_close'}
