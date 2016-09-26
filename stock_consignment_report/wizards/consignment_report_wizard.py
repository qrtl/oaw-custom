# -*- coding: utf-8 -*-
# Copyright 2016 Rooms For (Hong Kong) Limited T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields


class ConsignmentReportWizard(models.TransientModel):
    _name = "consignment.report.wizard"
    _description = 'Consignment Report Wizard'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partners',
    )
    threshold_date = fields.Date(
        required=True,
        string='Threshold Date',
    )


    @api.multi
    def action_export_xlsx(self):
        self.ensure_one()
        return self._export(xlsx_report=True)

    def _prepare_report_xlsx(self):
        self.ensure_one()
        # self.partner_ids = self.env['res.partner'].search([])
        return {
            'filter_partner_id': self.partner_id.id,
            'threshold_date': self.threshold_date
        }

    def _export(self, xlsx_report=False):
        model = self.env['consignment_report']
        report = model.create(self._prepare_report_xlsx())
        return report.print_report(xlsx_report)
