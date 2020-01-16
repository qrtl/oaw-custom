
import openerp
from openerp.osv import fields, osv


class account_voucher_line_ext(osv.osv):
    _inherit = "account.voucher"
