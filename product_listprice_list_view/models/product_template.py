# Copyright 2019 chrono123 & Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    additional_info = fields.Char(
        string= 'Note Internal',
    )
    # Resetting Offer Checked Button
    partner_offer_checked = fields.Boolean(
        string='Offer Checked',
        default=False,
    )
    qty_up = fields.Boolean(
        string='Quantity increased',
    )
    qty_down = fields.Boolean(
        string='Quantity decreased',
    )
    costprice_up = fields.Boolean(
        string='Costprice increased',
    )
    costprice_down = fields.Boolean(
        string='Costprice decreased',
        readonly=True,
    )
    note_updated = fields.Boolean(
        string='Partner Note updated',
    )

    @api.multi
    def write(self, vals):
        for product in self:
            # Resetting Offer Checked Button
            if 'qty_local_stock' in vals and 'qty_reserved' in vals:
                if vals['qty_local_stock'] - vals['qty_reserved'] == 0:
                    vals['partner_offer_checked'] = False
            elif 'qty_local_stock' in vals:
                if vals['qty_local_stock'] - product.qty_reserved == 0:
                    vals['partner_offer_checked'] = False
        return super(ProductTemplate, self).write(vals)
