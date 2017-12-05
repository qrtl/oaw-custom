# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class PartnerStatementReportWizard(models.TransientModel):
    _name = 'partner.statement.report.wizard'
    _inherit = 'account.common.partner.report'

    amount_currency = fields.Boolean(
        "With Currency",
        default=True,
        help="It adds the currency column"
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Filter on partner',
        help="Only selected partners will be printed. "
             "Leave empty to print all partners.",
    )
    filter = fields.Selection(
        [('filter_no', 'No Filters'),
         ('filter_date', 'Date'),
         ('filter_period', 'Periods')], "Filter by",
        required=True,
        help='Filter by date: no opening balance will be displayed. '
             '(opening balance can only be computed based on period to be \
             correct).',
    )

    def xls_export(self, cr, uid, ids, context=None):
        return self.check_report(cr, uid, ids, context=context)

    def _print_report(self, cr, uid, ids, data, context=None):
        # we update form with display account value
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        return {'type': 'ir.actions.report.xml',
                'report_name': 'account.account_report_partner_statement_report_xls',
                'datas': data}

    def pre_print_report(self, cr, uid, ids, data, context=None):
        data = super(PartnerStatementReportWizard, self).pre_print_report(
            cr, uid, ids, data, context=context)
        if context is None:
            context = {}
        # will be used to attach the report on the main account
        data['ids'] = [data['form']['chart_account_id']]
        vals = self.read(cr, uid, ids,
                         ['amount_currency', 'partner_ids'],
                         context=context)[0]
        data['form'].update(vals)
        return data
