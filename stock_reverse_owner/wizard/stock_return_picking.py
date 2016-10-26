# -*- coding: utf-8 -*-
# Copyright 2016 Rooms For (Hong Kong) Limited T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class stock_return_picking(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.model
    def _get_picking_default(self):
        return self._context and self._context.get('active_id', False) or False

    @api.one
    @api.depends('picking_id')
    def _get_type(self):
        self.picking_type_id = self.picking_id.picking_type_id.code

    return_category = fields.Selection(
        [('repair', 'Repair'),
        ('return_company', 'Return (Company)'),
        # ('return_vci', 'Return (VCI)'),
        ('return_no_ownership_change', 'Return (No Ownership Change)')],
        string='Return Category',
        # default='return_no_ownership_change',
        # required=True,
    )
    # supplier_id = fields.Many2one(
    #     'res.partner',
    #     string='Supplier',
    #     domain="[('supplier', '=', 1)]",
    # )
    picking_id = fields.Many2one(
        'stock.picking',
        string='Picking',
        default=_get_picking_default,
    )
    picking_type_id = fields.Char(
        'Picking Type',
        compute=_get_type,
    )

    # @api.one
    # @api.onchange('return_category')
    # def onchange_return_category(self):
    #     if self.return_category == 'return_vci':
    #         active_ids =  self.env.context.get('active_ids', [])
    #         picking_ids = self.env['stock.picking'].browse(active_ids)
    #         for picking in picking_ids:
    #             for move in picking.move_lines:
    #                 if move.reserved_quant_ids:
    #                     for quant in move.reserved_quant_ids:
    #                         if quant.owner_id:
    #                             self.supplier_id = quant.owner_id

    @api.multi
    def _create_returns(self):
        # for data in self:
        #     warning = True
        #     if data.return_category == 'return_vci':
        #         for move in data.product_return_moves:
        #             if move.move_id and \
        #                     move.move_id.quant_owner_id == self.supplier_id:
        #                 warning = False
        #                 break
        #     else:
        #         warning = False
        #     if warning:
        #         raise Warning (_('You cannot process return with \
        #             return category Return (VCI) when no Case Number \
        #             is owned by the selected Supplier.'))
        new_picking, picking_type_id = super(stock_return_picking, self).\
            _create_returns()

        # this part of the logic is borrowed from stock_account module
        for data in self:
            if data.invoice_state == '2binvoiced':
                picking = self.env['stock.picking'].browse(new_picking)
                for line in picking.move_lines:
                    line.write({'invoice_state': '2binvoiced'})

        picking = self.env['stock.picking'].browse(new_picking)
        for rec in self:
            picking.return_category = rec.return_category
            if rec.return_category == 'repair':
                picking.owner_id = picking.partner_id.id
            elif rec.return_category == 'return_company':
                picking.owner_id = picking.company_id.partner_id.id
            # elif rec.return_category == 'return_vci':
            #     picking.owner_id = rec.supplier_id.id
            else:
                pass  # odoo standard case
        return new_picking, picking_type_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
