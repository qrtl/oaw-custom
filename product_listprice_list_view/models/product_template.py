# Copyright 2019 chrono123 & Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    additional_info = fields.Char(
        String= 'Additional Info'
    )

    # For a filter in Product and Product Offer views.
    # Trigger: VCI Receipt (stock.quant (stock_move.purchase_price_unit)),
    # Supplier Stock Creation/Modification (supplier_stock.price_unit)
    currency_price_change_date = fields.Datetime(
        string="Currency Amount Price Change Date",
        store=True,
    )
    # For Filter Retail Changed 24H
    # Effective in Product and Product Offer
    # Trigger: product_template.list_price "Retail HKD"
    list_price_change_date = fields.Datetime(
        string="Retail HKD Change Date",
        store=True,
        compute="update_list_price_change_date"
    )
    # Trigger: stock_quant.create(), supplier_stock.create()
    new_entry_date = fields.Datetime(
        string="New Entry",
        store=True,
    )
    # Resetting Offer Checked Button
    partner_offer_checked = fields.Boolean(
        string='Offer Checked',
        default=False,
        store=True
    )
    qty_up = fields.Boolean(
        string='Partner Quantity increased',
        store=True
    )
    qty_down = fields.Boolean(
        string='Partner Quantity decreased',
        store=True
    )
    costprice_up = fields.Boolean(
        string='Partner Sale Price inc.',
        readonly=True,
        store=True
    )
    costprice_down = fields.Boolean(
        string='Partner Sale Price dec.',
        readonly=True,
        store=True
    )
    note_updated = fields.Boolean(
        string='Partner Note updated',
        store=True
    )
    # For a filter in Product and Product Offer
    # Trigger: product_template.write(),
    # Trigger: product_product.price_up_date
    price_up_date = fields.Datetime(
        string="Sale HKD Price Up Date",
        store=True,
    )
    # For a filter in Product and Product Offer
    # Trigger: product_template.write(),
    # Trigger: product_product.price_up_date
    price_down_date = fields.Datetime(
        string="Sale HKD Price Down Date",
        store=True,
    )

    @api.multi
    @api.depends('list_price')
    def update_list_price_change_date(self):
        for pt in self:
            pt.list_price_change_date = fields.Datetime.now()

    @api.multi
    def write(self, vals):
        for pt in self:
            # For a filter based on the date when AA price has been changed.
            if 'net_price' in vals:
                curr_net_price = pt.net_price
                if curr_net_price < vals['net_price']:
                    vals['price_up_date'] = fields.Datetime.now()
                elif curr_net_price > vals['net_price']:
                    vals['price_down_date'] = fields.Datetime.now()
            # Resetting Offer Checked Button
            if 'qty_local_stock' in vals and 'qty_reserved' in vals:
                if vals['qty_local_stock'] - vals['qty_reserved'] == 0:
                    vals['partner_offer_checked'] = False
                    self.partner_offer_checked = False
            elif 'qty_local_stock' in vals:
                if vals['qty_local_stock'] - pt.qty_reserved == 0:
                    vals['partner_offer_checked'] = False
        return super(ProductTemplate, self).write(vals)
