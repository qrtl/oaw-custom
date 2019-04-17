# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, osv
from odoo.tools.translate import _
from odoo.fields import Many2one

class product_template(models.Model):
    _inherit = 'product.template'

    def get_product_accounts(self, cr, uid, product_id, context=None):
        res = super(product_template,self).get_product_accounts(cr, uid, product_id, context=context)
        product_obj = self.browse(cr, uid, product_id, context=context)
        expense_acc = product_obj.property_account_expense and product_obj.property_account_expense.id or False
        if not expense_acc:
            expense_acc = product_obj.categ_id.property_account_expense_categ and product_obj.categ_id.property_account_expense_categ.id or False
        if not expense_acc:
            raise osv.except_osv(_('Error!'), _('''Expense Account cannot be identified.'''))
        res['expense_acc'] = expense_acc
        return res
