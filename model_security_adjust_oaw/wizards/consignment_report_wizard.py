# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class ConsignmentReportWizard(models.TransientModel):
    _inherit = "consignment.report.wizard"

    def _prepare_report_xlsx(self):
        data = super(ConsignmentReportWizard, self)._prepare_report_xlsx()
        if not self.env.user.has_group('stock.group_stock_user'):
            data['filter_partner_id'] = self.env.user.partner_id.id
        return data
