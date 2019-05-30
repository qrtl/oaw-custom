# Copyright 2019 chrono123 & Quartile
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"

    additional_info = fields.Char(
        String= 'Additional Info'
    )
    # Resetting Offer Checked Button
    partner_offer_checked = fields.Boolean(
        string='Offer Checked',
        default=False,
        store=True
    )
    qty_up = fields.Boolean(
        string='Quantity increased',
        store=True

    )
    qty_down = fields.Boolean(
        string='Quantity decreased',
        store=True
    )

    costprice_up = fields.Boolean(
        string='Costprice increased',
        readonly=True,
        store=True
    )
    costprice_down = fields.Boolean(
        string='Costprice decreased',
        readonly=True,
        store=True
    )
    note_updated = fields.Boolean(
        string='Partner Note updated',
        store=True

    )



    @api.multi
    def write(self, vals):
        for pt in self:
            # Resetting Offer Checked Button
            if 'qty_local_stock' in vals and 'qty_reserved' in vals:
                if vals['qty_local_stock'] - vals['qty_reserved'] == 0:
                    vals['partner_offer_checked'] = False
                    self.partner_offer_checked = False
            elif 'qty_local_stock' in vals:
                if vals['qty_local_stock'] - pt.qty_reserved == 0:
                    vals['partner_offer_checked'] = False
        return super().write(vals)