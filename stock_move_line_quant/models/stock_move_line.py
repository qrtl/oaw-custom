# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    origin_returned_move_id = fields.Many2one(
        related='move_id.origin_returned_move_id',
    )
    code = fields.Selection(
        related='move_id.picking_type_id.code',
    )
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

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        if self.currency_id:
            self.exchange_rate = self.currency_id.rate

    @api.multi
    @api.depends('purchase_price_unit', 'currency_id', 'exchange_rate')
    def _compute_price_unit(self):
        for move_line in self:
            if move_line.purchase_price_unit and move_line.exchange_rate:
                move_line.price_unit = move_line.purchase_price_unit / \
                                       move_line.exchange_rate

    @api.multi
    def write(self, vals):
        res = super(StockMoveLine, self).write(vals)
        for move_line in self:
            if move_line.move_id.purchase_line_id:
                if move_line.code == 'incoming' and \
                        move_line.purchase_price_unit != 0.0:
                    raise UserError(_('You are not allowed to update '
                                      'purchase price if the receipt '
                                      'refers to a purchase order.'))
            else:
                if move_line.code == 'incoming' and \
                        move_line.purchase_price_unit == 0.0 and not \
                        move_line.origin_returned_move_id:
                    raise UserError(_('Purchase price must be provided.'))
        return res

    def _action_done(self):
        res = super(StockMoveLine, self)._action_done()
        for move_line in self:
            if move_line.lot_id and move_line.code == 'incoming' and not \
                    move_line.origin_returned_move_id:
                move_line.lot_id.sudo().update({
                    'currency_id': move_line.currency_id.id,
                    'purchase_price_unit': move_line.purchase_price_unit,
                    'original_owner_id': move_line.owner_id.id or False,
                    'exchange_rate': move_line.exchange_rate,
                })
        return res
