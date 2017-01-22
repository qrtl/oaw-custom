# -*- coding: utf-8 -*-
# Copyright 2016-2017 Rooms For (Hong Kong) Limited T/A OSCG
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
        default=3,
    )
    stock_threshold_date = fields.Date(
        required=True,
        string='Stock Threshold Date',
        default=fields.Date.to_string(
            datetime.now() - relativedelta(days=90)),
    )
    cny_rate = fields.Float(
        required=True,
        digits=(12, 6),
        string='CNY Rate',
        default=lambda self: self._get_cny_rate(),
    )


    def _get_cny_rate(self):
        curr_obj = self.env['res.currency']
        cny_curr = curr_obj.search([('name', '=', 'CNY')])
        return cny_curr.rate_silent

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
            'cny_rate': self.cny_rate,
        }
