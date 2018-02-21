# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from openerp import models, fields, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class PartnerStatementReportWizard(models.TransientModel):
    _inherit = 'partner.statement.report.wizard'

    result_selection = fields.Selection(
        [('customer', 'Receivable Accounts'),
         ('supplier', 'Payable Accounts'),
         ('customer_supplier', 'Receivable and Payable Accounts')],
        "Partner's",
        default='customer_supplier',
        required=True,
    )

    def onchange_date(self, cr, uid, ids, date_from, date_to):
        if date_from:
            if datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT).date() \
                    < datetime.now().date().replace(month=1, day=1):
                return {
                    'value': {'date_from': False},
                    'warning': {
                        'title': _('Date Error'),
                        'message': _('The date must be within one year of '
                                     'today.')}
                }
        if date_to:
            if datetime.strptime(date_to, DEFAULT_SERVER_DATE_FORMAT).date() \
                > datetime.now().date().replace(month=12, day=31):
                return {
                    'value': {'date_to': False},
                    'warning': {
                        'title': _('Date Error'),
                        'message': _('The date must be within one year of '
                                     'today.')}
                }
        if date_from and date_to and date_from > date_to:
            return {
                'value': {'date_to': False, 'date_from': False},
                'warning': {
                    'title': _('Date Error'),
                    'message': _('The Start Date must be before the End '
                                 'Date.')}
            }
        return True
