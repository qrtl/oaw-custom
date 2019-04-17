# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ConsignmentReportWizard(models.TransientModel):
    _inherit = "consignment.report.wizard"

    def _prepare_report_xlsx(self):
        data = super(ConsignmentReportWizard, self)._prepare_report_xlsx()
        if self.env.user.has_group('model_security_adjust_oaw.group_supplier'):
            data['filter_partner_id'] = self.env.user.partner_id.id
        return data
