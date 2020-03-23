#Copyright 2019 chrono123 & Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


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
        not_invers = False
        for pp in self:
            if pp.product_tmpl_id.partner_offer_checked:
                continue
            if not pp.product_tmpl_id.partner_offer_checked:
                not_invers = True
                pp.product_tmpl_id.partner_offer_checked = True
        if not not_invers:
            for pp in self:
               pp.product_tmpl_id.partner_offer_checked = False