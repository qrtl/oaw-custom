# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"

    qty_local_stock = fields.Integer(
        string="Quantity Local Stock",
        readonly=True,
        help="Quantity on hand plus incoming quantity from stock moves that "
        'are "Available" ("assigned") state.',
        copy=False,
    )
    local_stock_not_reserved = fields.Integer(
        string="Local Stock",
        compute="_get_local_stock_not_reserved",
        store=True,
        readonly=True,
    )
    qty_reserved = fields.Integer(string="Quantity Reserved", readonly=True, copy=False)
    qty_overseas = fields.Integer(string="Quantity Overseas", readonly=True, copy=False)
    last_in_date = fields.Datetime(string="Last Incoming Date", readonly=True)
    local_stock = fields.Char(
        string="Local Stock", compute="_get_local_stock", store=True, readonly=True
    )
    overseas_stock = fields.Char(
        string="Overseas Stock",
        compute="_get_overseas_stock",
        store=True,
        readonly=True,
    )
    qty_local_own_stock = fields.Integer(
        string="Quantity Local Stock", compute="_get_qty_local_own_stock", store=True
    )
    stock_location = fields.Char(
        string="Stock Location", compute="_get_stock_location", store=True
    )
    stock_leadtime = fields.Char(
        string="Stock Lead Time", compute="_get_stock_location"
    )
    partner_note = fields.Text(string="Partner Note", compute="_get_stock_location")
    retail_of_cheapest = fields.Float(
        string="Stock Cost",
        compute="_get_stock_location",
        digits=dp.get_precision("Product Price"),
    )
    curr_of_cheapest = fields.Char(string="Currency", compute="_get_stock_location")

    @api.multi
    @api.depends("qty_local_stock")
    def _get_local_stock(self):
        for pt in self:
            if pt.qty_local_stock > 0:
                pt.local_stock = "Yes"
            else:
                pt.local_stock = "No"

    @api.multi
    @api.depends("qty_local_stock", "qty_reserved")
    def _get_local_stock_not_reserved(self):
        for pt in self:
            pt.local_stock_not_reserved = pt.qty_local_stock - pt.qty_reserved

    @api.multi
    @api.depends("qty_overseas")
    def _get_overseas_stock(self):
        for pt in self:
            if pt.qty_overseas > 0:
                pt.overseas_stock = "Yes"
            else:
                pt.overseas_stock = "No"

    @api.multi
    @api.depends("qty_local_stock")
    def _get_qty_local_own_stock(self):
        for pt in self:
            supplier_local_qty = 0
            if pt.product_variant_ids:
                supplier_stocks = (
                    self.env["supplier.stock"]
                    .sudo()
                    .search(
                        [
                            ("product_id", "in", pt.product_variant_ids.ids),
                            ("quantity", "!=", 0),
                            ("hk_location", "=", True),
                        ]
                    )
                )
                for ss in supplier_stocks:
                    supplier_local_qty += ss.quantity
            pt.qty_local_own_stock = pt.qty_local_stock - supplier_local_qty

    def _get_local_location_name(self, prod_ids):
        quant = self.env["stock.quant"].search(
            [("product_id", "in", prod_ids), ("usage", "=", "internal")],
            order="cost",
            limit=1,
        )
        return quant.location_id.name

    def _get_overseas_location_name(self, prod_ids):
        ss_obj = self.env["supplier.stock"]
        ss_recs = ss_obj.sudo().search(
            [("product_id", "in", prod_ids), ("quantity", ">", 0)]
        )
        lowest_cost = 0.0
        lowest_cost_ss_rec = False
        for ss_rec in ss_recs:
            if not lowest_cost or ss_rec.price_unit_base < lowest_cost:
                lowest_cost = ss_rec.price_unit_base
                lowest_cost_ss_rec = ss_rec
        if lowest_cost_ss_rec:
            loc = lowest_cost_ss_rec.partner_loc_id.name
            supp_lt = lowest_cost_ss_rec.supplier_lead_time
            partner_note = lowest_cost_ss_rec.partner_note
            retail_of_cheapest = lowest_cost_ss_rec.retail_in_currency
            curr_of_cheapest = lowest_cost_ss_rec.currency_id.name

            return loc, supp_lt, partner_note, retail_of_cheapest, curr_of_cheapest
        else:
            return False, False, False, False, False

    @api.multi
    def _get_stock_location(self):
        for pt in self:
            prod_ids = [p.id for p in pt.product_variant_ids]
            pt.stock_leadtime = "/"
            if pt.overseas_stock == "Yes":
                pt.stock_location, supp_lt, pt.partner_note, pt.retail_of_cheapest, pt.curr_of_cheapest = self._get_overseas_location_name(
                    prod_ids
                )
                pt.stock_leadtime = str(supp_lt) + " day(s)"
            if pt.local_stock == "Yes":
                local_location_name = self._get_local_location_name(prod_ids)
                if pt.overseas_stock == "Yes":
                    if local_location_name:
                        pt.stock_location += ", " + local_location_name
                else:
                    pt.stock_location = local_location_name
                    pt.stock_leadtime = "0 day(s)"
