# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    currency_id = fields.Many2one("res.currency", string="Purchase Currency")
    exchange_rate = fields.Float("FX Rate", digits=(12, 6))
    purchase_price_unit = fields.Float(
        "Purchase Currency Price", digits_compute=dp.get_precision("Product Price")
    )
    price_unit = fields.Float(
        "Unit Price",
        digits=dp.get_precision("Product Price"),
        compute="_compute_price_unit",
        store=True,
    )
    code = fields.Selection(
        related="move_id.picking_type_id.code", string="Type of Operation", store=True
    )
    quant_id = fields.Many2one("stock.quant", string="Stock Quant")

    @api.onchange("currency_id")
    def _onchange_currency_id(self):
        if self.currency_id:
            self.exchange_rate = self.currency_id.rate

    @api.onchange("quant_id")
    def _onchange_quant_id(self):
        if self.quant_id:
            self.lot_id = self.quant_id.lot_id
            self.owner_id = self.quant_id.owner_id

    @api.multi
    @api.depends("purchase_price_unit", "currency_id", "exchange_rate")
    def _compute_price_unit(self):
        for move_line in self:
            if move_line.purchase_price_unit and move_line.exchange_rate:
                move_line.price_unit = (
                    move_line.purchase_price_unit / move_line.exchange_rate
                )

    def _action_done(self):
        res = super(StockMoveLine, self)._action_done()
        for move_line in self:
            if (
                move_line.lot_id
                and move_line.move_id.picking_type_id.code == "incoming"
                and not move_line.move_id.location_id.return_location
            ):
                move_line.lot_id.sudo().update(
                    {
                        "currency_id": move_line.currency_id.id,
                        "purchase_price_unit": move_line.purchase_price_unit,
                        "original_owner_id": move_line.owner_id.id or False,
                        "exchange_rate": move_line.exchange_rate,
                    }
                )
        return res

    @api.model
    def create(self, vals):
        # Pass owner and purchase currency to create stock.move.line when it
        # is a receipt
        if "picking_id" in vals and "move_id" in vals:
            picking = self.env["stock.picking"].browse(vals["picking_id"])
            move = self.env["stock.move"].browse(vals["move_id"])
            if move.picking_type_id.code == "incoming" and not move.location_id.return_location:
                if picking.owner_id and "owner_id" not in vals:
                    vals["owner_id"] = picking.owner_id.id
                if move.currency_id:
                    vals["currency_id"] = move.currency_id.id
                    vals["exchange_rate"] = move.currency_id.rate
        res = super(StockMoveLine, self).create(vals)
        # Update the reservation_id of the stock quant
        if res.quant_id and res.move_id:
            res.quant_id.sudo().update({"reservation_id": res.move_id.id})
        return res

    @api.multi
    def write(self, vals):
        # Update the reservation_id of the stock quant
        if "quant_id" in vals:
            for move_line in self:
                move_line.quant_id.sudo().update({"reservation_id": False})
                self.env["stock.quant"].sudo().browse(vals["quant_id"]).update(
                    {"reservation_id": move_line.move_id.id}
                )
        res = super(StockMoveLine, self).write(vals)
        for move_line in self:
            if move_line.move_id.purchase_line_id:
                if (
                    move_line.move_id.picking_type_id.code == "incoming"
                    and move_line.purchase_price_unit != 0.0
                ):
                    raise UserError(
                        _(
                            "You are not allowed to update "
                            "purchase price if the receipt "
                            "refers to a purchase order."
                        )
                    )
            else:
                if (
                    move_line.move_id.picking_type_id.code == "incoming"
                    and move_line.move_id.location_id.usage != "customer"
                    and move_line.purchase_price_unit == 0.0
                    and not move_line.move_id.origin_returned_move_id
                ):
                    raise UserError(_("Purchase price must be provided."))
        return res

    @api.multi
    def unlink(self):
        # Update the reservation_id of the stock quant
        for move_line in self:
            if move_line.quant_id:
                move_line.quant_id.sudo().update({"reservation_id": False})
        return super(StockMoveLine, self).unlink()
