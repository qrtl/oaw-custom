# # Copyright 2019 Quartile Limited, Timeware Limited
# # License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
# from odoo import models, fields, api
#
#
# class ProductTemplate(models.Model):
#     _inherit = 'product.template'
#     @api.multi
#     def write(self, vals):
#         res = super(ProductTemplate, self).write(vals)
#         if 'name' in vals:
#             for pt in self:
#                 # Get the stock.transfer_details_items object
#                 transfer_details_items_object = self.env['stock.transfer_details_items']
#                 domain = [('product_id', 'in', pt.product_variant_ids.ids)]
#                 items = transfer_details_items_object.search(domain)
#                 for item in items:
#                     item.sudo().write({'new_description': pt.name})
#
#         return res
#
#
#
#
#
#
#
