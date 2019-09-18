# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    return_category = fields.Selection(
        [('repair', 'Repair'),
         ('return_company', 'Return (Company)'),
         ('return_no_ownership_change', 'Return (No Ownership Change)')],
        string='Return Category',
    )
    picking_id = fields.Many2one(
        'stock.picking',
        string='Picking',
        default=lambda self: self.env.context.get('active_id', False),
    )
    picking_type_id = fields.Char(
        'Picking Type',
        compute="compute_picking_type_id",
    )

    @api.multi
    def compute_picking_type_id(self):
        for picking in self:
            picking.picking_type_id = picking.picking_id.picking_type_id.code

    @api.multi
    def _create_returns(self):
        new_picking_id, pick_type_id = super(
            StockReturnPicking, self)._create_returns()
        new_picking = self.env['stock.picking'].browse(new_picking_id)
        # for picking in self:
        # if picking.invoice_state == '2binvoiced':
        #     for line in new_picking.move_lines:
        #         line.write({'invoice_state': '2binvoiced'})
        # new_picking.return_category = picking.return_category
        # if picking.return_category == 'repair':
        #     picking.owner_id = new_picking.partner_id.id
        # elif picking.return_category == 'return_company':
        #     picking.owner_id = new_picking.company_id.partner_id.id
        return new_picking_id, pick_type_id
