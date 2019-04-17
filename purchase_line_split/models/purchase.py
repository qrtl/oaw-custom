# -*- coding: utf-8 -*-
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016 Rooms For (Hong Kong) Limited T/A OSCG
#    <https://www.odoo-asia.com>
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

from odoo import fields, osv
from odoo.tools.translate import _


class purchase_order(models.Model):
    _inherit = "purchase.order"

    def action_button_split_line(self, cr, uid, ids, context=None):
        context = context or {}
        for purchase in self.browse(cr, uid, ids, context=context):
            if not purchase.order_line:
                raise osv.except_osv(_('Error!'),_('You cannot split a purchase order which has no line.'))
            for line in purchase.order_line:
                if line.product_id.product_tmpl_id.categ_id.enforce_qty_1 and line.product_qty > 1.0:
                    for qty in range(0, int(line.product_qty - 1)):
                        default = {'product_qty': 1.0}
                        self.pool.get('purchase.order.line').copy(cr, uid, line.id, default=default, context=context)
                    self.pool.get('purchase.order.line').write(cr, uid, [line.id], {'product_qty': 1.0}, context=context)
            self.write(cr, uid, [purchase.id], {'need_auto_split': False}, context=context)
        return True

    def _need_auto_split(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for purchase in self.browse(cr, uid, ids, context=context):
            res[purchase.id] = False
            for line in purchase.order_line:
                if line.product_id.product_tmpl_id.categ_id.enforce_qty_1 and line.product_qty > 1.0:
                    res[purchase.id] = True
        return res

    _columns = {
        'need_auto_split': fields.function(_need_auto_split, string='Need Auto Split?',
            type='boolean', store={
            'purchase.order': (lambda self, cr, uid, ids, c={}: ids, [], 10),
            },),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
