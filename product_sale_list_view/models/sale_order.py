# Copyright 2020  Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"
    # Clean version - handing over the vals dictionary to the method
    @api.multi
    def _update_prod_tmpl_amount_and_average(self):
        for sol in self.order_line:
            Rate = self.env["res.currency.rate"]
            date = sol.order_id.date_order
            rate = 1.0
            if (
                date
                and sol.order_id.currency_id != self.env.user.company_id.currency_id
            ):
                rate = (
                    Rate.search(
                        [
                            ("currency_id", "=", sol.order_id.currency_id.id),
                            ("name", "<=", date),
                        ],
                        order="name desc",
                        limit=1,
                    ).rate
                    or 1.0
                )
            sol.subtotal_hkd = sol.price_subtotal / rate
            sol.product_id.product_tmpl_id.total += sol.subtotal_hkd
            sol.product_id.product_tmpl_id.counts += sol.product_uom_qty

    @api.multi
    def write(self, vals):
        if "state" in vals and vals["state"] == "sale":
            self._update_prod_tmpl_amount_and_average()
        return super(SaleOrder, self).write(vals)
