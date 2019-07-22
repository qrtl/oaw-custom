# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    currency_id = fields.Many2one(
        'res.currency',
        string='Purchase Currency',
    )
    exchange_rate = fields.Float(
        'FX Rate',
        digits=(12, 6),
    )
    purchase_price_unit = fields.Float(
        'Purchase Currency Price',
        digits_compute=dp.get_precision('Product Price'),
    )
    price_unit = fields.Float(
        'Unit Price',
        digits=dp.get_precision('Product Price'),
        compute='_compute_price_unit',
        store=True,
    )
    code = fields.Selection(
        related='move_id.picking_type_id.code',
        string='Type of Operation',
        store=True,
    )
    quant_id = fields.Many2one(
        'stock.quant',
        string='Stock Quant',
    )

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        if self.currency_id:
            self.exchange_rate = self.currency_id.rate

    @api.onchange('quant_id')
    def _onchange_quant_id(self):
        if self.quant_id:
            self.lot_id = self.quant_id.lot_id

    @api.multi
    @api.depends('purchase_price_unit', 'currency_id', 'exchange_rate')
    def _compute_price_unit(self):
        for move_line in self:
            if move_line.purchase_price_unit and move_line.exchange_rate:
                move_line.price_unit = move_line.purchase_price_unit / \
                    move_line.exchange_rate

    def _action_done(self):
        res = super(StockMoveLine, self)._action_done()
        for move_line in self:
            if move_line.lot_id:
                move_line.lot_id.sudo().update({
                    'currency_id': move_line.currency_id.id,
                    'purchase_price_unit': move_line.purchase_price_unit,
                    'original_owner_id': move_line.owner_id.id or False,
                    'exchange_rate': move_line.exchange_rate,
                })
        return res

    @api.model
    def create(self, vals):
        if 'picking_id' in vals:
            picking = self.env['stock.picking'].browse(vals['picking_id'])
            if picking.owner_id:
                vals['owner_id'] = picking.owner_id.id
            if picking.purchase_currency_id:
                vals['currency_id'] = picking.purchase_currency_id.id
                vals['exchange_rate'] = picking.purchase_currency_id.rate
        res = super(StockMoveLine, self).create(vals)
        if res.quant_id and res.move_id:
            res.quant_id.sudo().update({
                'reservation_id': res.move_id.id
            })
        return res

    @api.multi
    def write(self, vals):
        if 'quant_id' in vals:
            for move_line in self:
                move_line.quant_id.sudo().update({
                    'reservation_id': False
                })
                self.env['stock.quant'].sudo().browse(vals['quant_id']).update({
                    'reservation_id': move_line.move_id.id
                })
        res = super(StockMoveLine, self).write(vals)
        for move_line in self:
            if move_line.move_id.purchase_line_id:
                if move_line.move_id.picking_type_id.code == 'incoming' and \
                        move_line.purchase_price_unit != 0.0:
                    raise UserError(_('You are not allowed to update '
                                      'purchase price if the receipt '
                                      'refers to a purchase order.'))
            else:
                if move_line.move_id.picking_type_id.code == 'incoming' and \
                        move_line.move_id.location_id.usage != 'customer' \
                        and move_line.purchase_price_unit == 0.0 and not \
                        move_line.move_id.origin_returned_move_id:
                    raise UserError(_('Purchase price must be '
                                      'provided.'))
        return res

    @api.multi
    def unlink(self):
        for move_line in self:
            if move_line.quant_id:
                move_line.quant_id.sudo().update({
                    'reservation_id': False
                })
        return super(StockMoveLine, self).unlink()
