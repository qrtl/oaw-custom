# -*- coding: utf-8 -*-
# Copyright 2016 Rooms For (Hong Kong) Limited T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import api, models, fields


class OfferReportWizard(models.TransientModel):
    _name = "offer.report.wizard"
    _description = 'Stock Offer Report Wizard'

    new_stock_days = fields.Integer(
        required=True,
        string='New Stock Days',
        default=1,
    )
    stock_threshold_date = fields.Date(
        required=True,
        string='Stock Threshold Date',
        default=fields.Date.to_string(
            datetime.now() - relativedelta(days=90)),

    )
    sales_threshold_date = fields.Date(
        required=True,
        string='Sales Threshold Date',
        default=fields.Date.to_string(
            datetime.now() - relativedelta(days=10)),
    )

    @api.multi
    def action_export_xlsx(self):
        self.ensure_one()
        model = self.env['offer.report']
        report = model.create(self._prepare_report_xlsx())
        return report.print_report()

    def _prepare_report_xlsx(self):
        self.ensure_one()
        return {
            'new_stock_days': self.new_stock_days,
            'stock_threshold_date': self.stock_threshold_date,
            'sales_threshold_date': self.sales_threshold_date,
        }
