
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp

class ProductCategory(models.Model):

    _inherit="product.category"

    supplier_access = fields.Boolean(
        'Available for Supplier',
        default = False,
        store=True,
    )

    @api.multi
    def name_get(self):

        context = self._context or {}
        print(context)
        if context.get('supplier_access_context',False):

            res =[]
            for cat in self:
                res.append(
                    (cat.id, cat.name)
                )
            return res
        else:
            return super(ProductCategory,self).name_get()