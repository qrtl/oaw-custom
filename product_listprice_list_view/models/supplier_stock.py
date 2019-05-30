# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SupplierStock(models.Model):
    _inherit = "supplier.stock"


    # Resetting Offer Checked Button
    def check_changes(self, vals):
        pt = self.product_id.product_tmpl_id
        if 'quantity' in vals:
            curr_quantity = self.quantity
            if curr_quantity < vals['quantity']:
                pt.sudo().write({'qty_up': True, 'partner_offer_checked': False})
            elif curr_quantity > vals['quantity']:
                pt.sudo().write({'qty_down': True, 'partner_offer_checked': False})
        if 'price_unit' in vals:
            curr_price_unit = self.price_unit
            if curr_price_unit < vals['price_unit']:
                pt.sudo().write({'costprice_up': True, 'partner_offer_checked': False})
            elif curr_price_unit > vals['price_unit']:
                pt.sudo().write({'costprice_down': True, 'partner_offer_checked': False})
        if 'partner_note' in vals:
            pt.sudo().write({'note_updated': True})


    @api.multi
    def write(self, vals):
        for ps in self:
            ps.check_changes(vals)
        return super().write(vals)
