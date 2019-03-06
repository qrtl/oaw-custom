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
