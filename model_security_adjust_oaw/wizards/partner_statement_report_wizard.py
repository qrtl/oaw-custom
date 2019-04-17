# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from odoo import models, fields, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


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
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        'Fiscal Year',
        required=True,
        help='Keep empty for all open fiscal year',
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

    def _get_fiscalyear(self, cr, uid, context=None):
        if str(self._model) == "partner.statement.report.wizard" and \
                self.pool.get('res.users').has_group(
                    cr, uid, 'model_security_adjust_oaw.group_supplier'):
            fiscalyears = self.pool.get('account.fiscalyear').search(
                cr, uid, [('allow_supplier_access', '=', True)], limit=1)
            fy =  fiscalyears and fiscalyears[0] or False
            return fy
        return super(PartnerStatementReportWizard, self)._get_fiscalyear(
            cr=cr, uid=uid, context=context)

    def onchange_chart_id(self, cr, uid, ids, chart_account_id=False, context=None):
        res = super(PartnerStatementReportWizard, self).onchange_chart_id(
            cr, uid, ids, chart_account_id, context)
        if not res.get('value', {}):
            res.update({'value': {}})
        if str(self._model) == "partner.statement.report.wizard":
            if chart_account_id and self.pool.get('res.users').has_group(
                    cr, uid, 'model_security_adjust_oaw.group_supplier'):
                fiscalyears = self.pool.get('account.fiscalyear').search(
                    cr, uid, [('allow_supplier_access', '=', True)], limit=1)
                fy =  fiscalyears and fiscalyears[0] or False
                res['value'].update({'fiscalyear_id': fy})
        return res

    _defaults = {
        'fiscalyear_id': _get_fiscalyear,
    }
