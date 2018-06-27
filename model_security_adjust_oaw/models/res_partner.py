from openerp import models, fields, api
from openerp import SUPERUSER_ID

class ResPartner(models.Model):
    _inherit = 'res.partner'

    product_category_ids = fields.Many2many(
        comodel_name ='product.category',
        string = 'Accessible Product Category'
    )

    related_partner = fields.Many2one(
        comodel_name='res.partner',
        string = "Related Partner"

    )

    @api.multi
    def write(self,vals):
        if 'product_category_ids' in vals:
            ir_rule= self.env.ref('model_security_adjust_oaw.res_partner_supplier_fm_product_rule')
            ir_rule.clear_caches()
        return super(ResPartner, self).write(vals)

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if self.pool['res.users'].has_group(
                cr, uid, 'model_security_adjust_oaw.group_supplier_fm') and \
                context.get('partner_sudo_search', False):
            return super(ResPartner, self).name_search(cr, SUPERUSER_ID, name,
                                                       args=args,
                                                       operator=operator,
                                                       context=context,
                                                       limit=limit)
        return super(ResPartner, self).name_search(cr, uid, name,
                                                   args=args,
                                                   operator=operator,
                                                   context=context,
                                                   limit=limit)
