# Copyright 2019 chrono123 & Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class SupplierStock(models.Model):
    _inherit = "supplier.stock"

    # Resetting Offer Checked Button
    def check_changes(self, vals):
        values = {}
        product = self.product_id.product_tmpl_id
        if 'quantity' in vals:
            curr_quantity = self.quantity
            if self.quantity < vals['quantity']:
                values.update(qty_up=True, partner_offer_checked=False)
            elif self.quantity > vals['quantity']:
                values.update(qty_down=True, partner_offer_checked=False)
        if 'price_unit' in vals:
            if self.price_unit < vals['price_unit']:
                values.update(costprice_up=True, partner_offer_checked=False)
            elif self.price_unit > vals['price_unit']:
                values.update(costprice_down=True, partner_offer_checked=False)
        if 'partner_note' in vals:
            values.update(note_updated=True)
        if values:
            product.sudo().write(values)

    @api.multi
    def write(self, vals):
        for ps in self:
            ps.check_changes(vals)
        return super(SupplierStock, self).write(vals)
