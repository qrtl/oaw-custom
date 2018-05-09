# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, osv, orm
from openerp import SUPERUSER_ID


class ProductProduct(osv.osv):
    _inherit = "product.product"

    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if context.get('supplier_access_context', False):
            res = []
            for product in self.browse(cr, SUPERUSER_ID, ids, context=context):
                res.append(
                    (product.id, product.name)
                )
            return res
        else:
            return super(ProductProduct, self).name_get(cr, user, ids,
                                                        context=context)
