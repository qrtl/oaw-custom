# -*- coding: utf-8 -*-
#    Odoo, Open Source Management Solution
#    Copyright (C) 2015-2016 Rooms For (Hong Kong) Limited T/A OSCG
#    <https://www.odoo-asia.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from openerp import models, fields, api, _
from datetime import datetime
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import SUPERUSER_ID
 

class StockMove(models.Model):
    _inherit = 'stock.move'

    pick_partner_id = fields.Many2one(
        related='picking_id.partner_id',
        store=True,
        readonly=True,
        string='Pick Partner'
        )
    quant_lot_id = fields.Many2one(
        'stock.production.lot',
        compute='_get_quant_info',
        store=True,
        readonly=True,
        string='Case No.'
        )
    quant_owner_id = fields.Many2one(
        'res.partner',
        compute='_get_quant_info',
        store=True,
        readonly=True,
        string='Owner'
        )
    so_id = fields.Many2one(
        'sale.order',
        compute='_get_vals',
        store=True,
        readonly=True,
        string='SO'
        )
    po_id = fields.Many2one(
        'purchase.order',
        compute='_get_vals',
        store=True,
        readonly=True,
        string='PO'
        )

    @api.multi
    @api.depends('quant_ids', 'lot_id')
    def _get_quant_info(self):
        for m in self:
            if m.quant_ids:
                m.quant_lot_id = m.quant_ids[0].lot_id and \
                    m.quant_ids[0].lot_id.id
                m.quant_owner_id = m.quant_ids[0].owner_id and \
                    m.quant_ids[0].owner_id.id
            else:
                m.quant_lot_id = m.lot_id.id
                # below part does not work since quant is generated after \
                # this step
#                 if m.lot_id.quant_ids:
#                     m.quant_owner_id = m.lot_id.quant_ids[-1].owner_id and \
#                         m.lot_id.quant_ids[-1].owner_id.owner_id.id

    @api.multi
    @api.depends('origin')
    def _get_vals(self):
        SO = self.env['sale.order']
        PO = self.env['purchase.order']
        for m in self:
            m.so_id, m.po_id = 0, 0
            if m.purchase_line_id:
                m.po_id = m.purchase_line_id.order_id.id
            elif m.procurement_id and m.procurement_id.sale_line_id:
                m.so_id = m.procurement_id.sale_line_id.order_id.id

    def init(self, cr):
        move_ids = self.search(cr, SUPERUSER_ID, [])
        for m in self.browse(cr, SUPERUSER_ID, move_ids):
            m.pick_partner_id = m.picking_id.partner_id and m.picking_id.partner_id.id
            if m.quant_ids:
                m.quant_lot_id = m.quant_ids[0].lot_id and m.quant_ids[0].lot_id.id
                m.quant_owner_id = m.quant_ids[0].owner_id and m.quant_ids[0].owner_id.id
