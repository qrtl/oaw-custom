# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.depends('move_line_ids', 'picking_type_id.use_create_lots', 'picking_type_id.use_existing_lots', 'state')
    def _compute_show_lots_text(self):
        group_production_lot_enabled = self.user_has_groups(
            'stock.group_production_lot')
        for picking in self:
            if not picking.move_line_ids:
                picking.show_lots_text = False
            # <<< QTL EDIT
            # Make lot_id always visible
            # elif group_production_lot_enabled and picking.picking_type_id.use_create_lots \
            #         and not picking.picking_type_id.use_existing_lots and picking.state != 'done':
            elif group_production_lot_enabled and picking.picking_type_id.use_create_lots \
                    and not picking.picking_type_id.use_existing_lots:
                picking.show_lots_text = True
            else:
                picking.show_lots_text = False
