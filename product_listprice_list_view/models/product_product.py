# Copyright 2019 chrono123 & Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.onchange("partner_offer_checked")
    def _onchange_partner_offer_checked(self):
        if self.partner_offer_checked:
            self.qty_down = False
            self.qty_up = False
            self.costprice_up = False
            self.costprice_down = False
            self.note_updated = False

    @api.multi
    def _check_offer_checked(self):
        for pp in self:
            if not pp.product_tmpl_id.partner_offer_checked:
                pp.product_tmpl_id.partner_offer_checked = True
            elif pp.product_tmpl_id.partner_offer_checked:
                pp.product_tmpl_id.partner_offer_checked = False
