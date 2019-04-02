# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_method = fields.Selection(
        selection=[
            ('cash', 'Cash'),
            ('china_bank_transfer', 'China Bank Transfer'),
            ('hk_bank_cheque', 'Hong Kong Banks\' Cheque'),
            ('direct_bank_transfer', 'Bank Transfer to our HK company'),
            ('visa_union_pay', 'Visa or Union (Extra 2.2% as fee)'),
            ('other', 'Other Payment Method'),
        ],
        string='Payment Method',
    )
    payment_desc = fields.Char(
        string='Other Payment Method',
    )
    picking_date = fields.Date(
        string='Desire Picking Date',
        help='Monday to Friday 15:00-18:00',
    )
    other_inquiry = fields.Char(
        string='Other Inquiry',
    )

    # According to the user group and price settings, update the price with
    # portal user adds product to cart.
    def _cart_update(self, product_id=None, line_id=None, add_qty=0,
                     set_qty=0):
        res = super(SaleOrder, self)._cart_update(product_id=product_id,
                                                  line_id=line_id,
                                                  add_qty=add_qty,
                                                  set_qty=set_qty)
        if 'line_id' in res and res['line_id']:
            order_line = self.env['sale.order.line'].browse(res['line_id'])
            product = order_line.product_id
            if product.sale_hkd_ac_so:
                order_line.price_unit = product.sale_hkd_ac_so
            else:
                if order_line.order_id.partner_id.user_ids and \
                        order_line.order_id.partner_id.user_ids[
                            0].has_group(
                            'website_timecheck.group_timecheck_light'):
                    order_line.price_unit = product.sale_hkd_ac
                elif product.qty_overseas != 0 and \
                        product.oversea_retail_currency_id == \
                        product.company_id.currency_id and product.price > \
                        product.oversea_retail_price:
                    order_line.price_unit = product.oversea_retail_price
                else:
                    order_line.price_unit = product.list_price
        return res


from openerp.osv import osv, fields


class SaleOrderOsv(osv.osv):
    _inherit = "sale.order"

    # print function for portal customer
    def print_portal_quotation(self, cr, uid, ids, context=None):
        return self.pool['report'].get_action(cr, uid, ids,
                                              'sale.report_saleorder',
                                              context=context)
