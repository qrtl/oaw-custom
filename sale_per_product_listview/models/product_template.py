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
        "Qty of Sale Order Lines",
        readonlu=True
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

    # object action for chrono update button in sale order form view
    @api.multi
    def action_view_sol_open(self):
        view_id = self.env.ref("base.view_users_form").id
        return {
            "name": "Supplier Users",
            "view_mode": "form",
            "view_type": "form",
            "res_model": "product_product",
            "view_id": view_id,
            "type": "ir.actions.act_window",
            "res_id": self.id,
            "target": "current",
            "domain": "[('product_id','in', self.product_variant_ids.ids),('state','=','sale')]"
        }


    # # Classical implementation of inline-button
    # @api.multi
    # def action_view_sales_ext(self):
    #     action = self.env.ref('oa_products_sales.report_all_channels_sales_action').read()[0]
    #     print(self.product_variant_ids.ids)
    #     # Regarding domain: Self is product template!
    #     # Left part is field of model the action bases on, i.e. sale.order.line!
    #     action['domain'] = [('product_id','in', self.product_variant_ids.ids),('state','=','sale')]
    #     #Domain in use when Sales Order is automatically locked
    #     #action['domain'] = [('product_id', 'in', self.product_variant_ids.ids), ('state', '=', 'done')]
    #     return action

    # Better implemtation, but momentarily not allowing setting the search_view_id of custom search view.
    # @api.multi
    # def action_view_sales_ext(self):
    #     view_id = self.env.ref('oa_products_sales.sale_order_line_tree_z2')
    #     search_view_id = self.env.ref('oa_products_sales.sale_order_line_tree_search')
    #     print(search_view_id.id)
    #     product_ids = [str(x.id) for x in self.product_variant_ids]
    #
    #     # print(','.join(product_ids))
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'sale.order.line',
    #         'name' : self.name,
    #         # view type not necessary anymore
    #         'view_mode': 'tree',
    #         'view_id': view_id.id,
    #         'context': {},
    #         'target': 'current',
    #         'domain': "[('product_id','in', [%s])]" % ','.join(product_ids),
    #         'search_view_id': search_view_id.id
    #     }