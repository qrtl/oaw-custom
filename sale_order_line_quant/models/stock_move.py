# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = "stock.move"

    quant_id = fields.Many2one(
        'stock.quant',
        string='Stock Quant',
    )
    lot_id = fields.Many2one(
        'stock.production.lot',
        string='Case No.',
    )
    quant_owner_id = fields.Many2one(
        related='quant_id.owner_id',
        store=True,
        readonly=True,
        string='Owner',
    )

    def action_show_details(self):
        res = super(StockMove, self).action_show_details()
        res['context'].update({
            'show_purchase_information': self.picking_type_id.code == 'incoming'
        })
        return res

    def _action_confirm(self):
        res = super(StockMove, self)._action_confirm()
        for move in self:
            if move.quant_id and not move.move_line_ids:
                values = {
                    'move_id': move.id,
                    'picking_id': move.picking_id.id,
                    'product_id': move.product_id.id,
                    'product_uom_id': move.product_uom.id,
                    'location_id': move.location_id.id,
                    'location_dest_id': move.location_dest_id.id,
                    'quant_id': move.quant_id.id,
                    'lot_id': move.lot_id.id,
                    'product_uom_qty': 1.0,
                    'qty_done': 1.0,
                }
                self.env['stock.move.line'].create(values)
                move.quant_id.reserved_quantity += 1
        return res
