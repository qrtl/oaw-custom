# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID
from odoo import fields, osv
from odoo.tools.translate import _
from odoo.report import report_sxw


class account_voucher(models.Model):
    _inherit = 'account.voucher'

    def _get_currency_help_label(self, cr, uid, currency_id, payment_rate, payment_rate_currency_id, context=None):
        """
        This function builds a string to help the users to understand the behavior of the payment rate fields they can specify on the voucher.
        This string is only used to improve the usability in the voucher form view and has no other effect.

        :param currency_id: the voucher currency
        :type currency_id: integer
        :param payment_rate: the value of the payment_rate field of the voucher
        :type payment_rate: float
        :param payment_rate_currency_id: the value of the payment_rate_currency_id field of the voucher
        :type payment_rate_currency_id: integer
        :return: translated string giving a tip on what's the effect of the current payment rate specified
        :rtype: str
        """
        rml_parser = report_sxw.rml_parse(cr, SUPERUSER_ID, 'currency_help_label', context=context)
        currency_pool = self.pool.get('res.currency')
        currency_str = payment_rate_str = ''
        if currency_id:
            currency_str = rml_parser.formatLang(1, currency_obj=currency_pool.browse(cr, uid, currency_id, context=context))
        if payment_rate_currency_id:
            payment_rate_str  = rml_parser.formatLang(payment_rate, currency_obj=currency_pool.browse(cr, uid, payment_rate_currency_id, context=context))
        currency_help_label = _('At the operation date, the exchange rate was\n%s = %s') % (currency_str, payment_rate_str)
        return currency_help_label
