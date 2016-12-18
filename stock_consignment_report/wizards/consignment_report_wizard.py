# -*- coding: utf-8 -*-
# Copyright 2016 Rooms For (Hong Kong) Limited T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import api, models, fields


class ConsignmentReportWizard(models.TransientModel):
    _name = "consignment.report.wizard"
    _description = 'Consignment Report Wizard'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        required=True,
        string='Partner',
    )
    threshold_date = fields.Date(
        required=True,
        string='Threshold Date',
        default=fields.Date.to_string(
            datetime.now() - relativedelta(days=180)),
    )

    @api.multi
    def action_export_xlsx(self):
        self.ensure_one()
        model = self.env['consignment_report']
        report = model.create(self._prepare_report_xlsx())
        return report.print_report()

    def _prepare_report_xlsx(self):
        self.ensure_one()
        return {
            'filter_partner_id': self.partner_id.id,
            'threshold_date': self.threshold_date
        }
