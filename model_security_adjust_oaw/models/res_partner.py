from openerp import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    product_category_ids = fields.Many2many(
        comodel_name ='product.category',
        string = 'Accessible Product Category'
    )

    @api.multi
    def write(self,vals):
        if 'product_category_ids' in vals:
            ir_rule= self.env.ref('model_security_adjust_oaw.res_partner_supplier_fm_product_rule')
            ir_rule.clear_caches()
        return super(ResPartner, self).write(vals)