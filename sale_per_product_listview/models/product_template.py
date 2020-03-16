# Copyright 2020  Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class product_template_ext(models.Model):
    _inherit = 'product.template'
    _description = 'Products Sale'

    total = fields.Float(
        string="Total HKD",
        digits=dp.get_precision('Product Price'),
        readonly=True
    )

    average = fields.Float(
        string="Average Price",
        digits=dp.get_precision('Product Price'),
        readonly=True,
        compute='_calc_average'
    )

    counts = fields.Integer(
        "Qty of all Sale Order Lines",
        readonly=True
    )

    @api.multi
    def _calc_average(self):
        for pt in self:
            if pt.counts != 0:
                pt.average = pt.total / pt.counts

    # triggered by More Button
    @api.multi
    def _initialize_values(self, pts):
        sol_object = self.env['sale.order.line']
        for pt in pts:
            domain = [
                ('product_id', '=', pt.product_variant_ids.ids),
                ('state', '=', 'sale'),
            ]
            sols = sol_object.search(domain)
            sols_len = len(sols)
            if sols_len != 0:
                pt.total = 0.0
                pt.counts = sols_len
                for sol in sols:
                    date = sol.order_id.date_order
                    rate = 1.0
                    if date and sol.order_id.currency_id != self.env.user.company_id.currency_id:
                        rate = self.env['res.currency.rate'].search([
                            ('currency_id', '=', sol.order_id.currency_id.id),
                            ('name', '<=', date),
                        ], order='name desc', limit=1).rate or 1.0

                    sol.subtotal_hkd = sol.price_subtotal / rate
                    print(sol.subtotal_hkd)
                    # Updating pt's total
                    pt.total += sol.subtotal_hkd

                # Updating pt's average
                pt.average = pt.total / pt.counts
        return

    @api.multi
    def action_view_sol_open(self):
        view_id = self.env.ref('sale_per_product_listview.sale_order_lines_tree').id
        return {
            #for better record representation, set the name
            'name': self.default_code,
            'view_mode': 'tree',
            'res_model': 'sale.order.line',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain' : [("product_id","in", self.product_variant_ids.ids)]     
        }
