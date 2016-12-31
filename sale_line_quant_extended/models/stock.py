# -*- coding: utf-8 -*-
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016 Rooms For (Hong Kong) Limited T/A OSCG
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


class StockMove(models.Model):
    _inherit = "stock.move"

    pick_partner_id = fields.Many2one(
        related='picking_id.partner_id',
        store=True,
        readonly=True,
        string='Pick Partner'
        )
    picking_type_code = fields.Selection(
        related='picking_type_id.code',
        store=True,
        readonly=True,
        string='Picking Type Code'
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
    is_mto = fields.Boolean('Make to Order',
        compute='_compute_mto',
        store=True,
        )


    @api.multi
    def name_get(self):
        res = []
        for line in self:
            name = line.location_id.name + ' > ' + line.location_dest_id.name
            if line.product_id.code:
                name = line.product_id.code + ': ' + name
            if line.picking_id.origin:
                pick_rec = self.env['stock.picking'].search(
                        [('name','=',line.picking_id.origin)])
                if pick_rec.picking_type_id.code == 'incoming':
                    name = line.picking_id.name + '/ ' + name
                else:
                    name = line.picking_id.origin + '/ ' + name
            res.append((line.id, name))
        return res


    @api.multi
    @api.depends('quant_ids', 'reserved_quant_ids', 'lot_id')
    def _get_quant_info(self):
        for m in self:
            if m.quant_ids:
                m.quant_lot_id = m.quant_ids[0].lot_id and \
                    m.quant_ids[0].lot_id.id
                m.quant_owner_id = m.quant_ids[0].owner_id and \
                    m.quant_ids[0].owner_id.id
            elif m.reserved_quant_ids:
                m.quant_lot_id = m.reserved_quant_ids[0].lot_id and \
                    m.reserved_quant_ids[0].lot_id.id
                m.quant_owner_id = m.reserved_quant_ids[0].owner_id and \
                    m.reserved_quant_ids[0].owner_id.id
            else:
                m.quant_lot_id = m.lot_id.id
                # below part does not work since quant is generated after \
                # this step
#                 if m.lot_id.quant_ids:
#                     m.quant_owner_id = m.lot_id.quant_ids[-1].owner_id and \
#                         m.lot_id.quant_ids[-1].owner_id.owner_id.id

    def _get_quant_info_init(self, cr, uid):
        # update quant info when installing/upgrading
        cr.execute("""
            update stock_move m1
            set quant_lot_id = lot, quant_owner_id = owner
            from (select q.lot_id as lot, q.owner_id as owner, m2.id as id
                  from stock_quant q
                  join stock_move m2 on q.reservation_id = m2.id) as subq
            where m1.id = subq.id
            and quant_lot_id is null
        """)


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


    @api.one
    @api.depends('procurement_id', 'purchase_line_id')
    def _compute_mto(self):
        if self.code == 'outgoing' and self.procurement_id and \
                self.procurement_id.sale_line_id:
            self.is_mto = self.procurement_id.sale_line_id.mto
        elif self.code == 'incoming' and self.purchase_line_id:
            self.is_mto = self.purchase_line_id.mto


    # def init(self, cr):
    #     move_ids = self.search(cr, SUPERUSER_ID, [])
    #     for m in self.browse(cr, SUPERUSER_ID, move_ids):
    #         m.pick_partner_id = m.picking_id.partner_id and m.picking_id.partner_id.id
    #         if m.quant_ids:
    #             m.quant_lot_id = m.quant_ids[0].lot_id and m.quant_ids[0].lot_id.id
    #             m.quant_owner_id = m.quant_ids[0].owner_id and m.quant_ids[0].owner_id.id

    @api.model
    def _prepare_picking_assign(self, move):
        res = super(StockMove, self)._prepare_picking_assign(move)
        res['is_mto'] = move.is_mto
        return res


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_mto = fields.Boolean(
        'Make to Order',
        )
    to_check = fields.Boolean(
        'To Be Checked',
        )


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.one
    @api.depends('sale_reserver_qty', 'sale_line_reserver_qty')
    def _actual_qty(self):
        if self.sale_reserver_qty:
            self.actual_qty = self.qty - self.sale_reserver_qty
        else:
            self.actual_qty = self.qty - self.sale_line_reserver_qty


    sale_line_id = fields.Many2one(
        'sale.order.line',
        readonly=True,
        string='Reserved for SO Line',
    )
    sale_line_reserver_qty = fields.Float(
        related='sale_line_id.product_uom_qty',
        store=True,
        readonly=True,
        string='Qty Reserved by SO'
    )
    sale_id = fields.Many2one(
        'sale.order',
        related='sale_line_id.order_id',
        store=True,
        readonly=True,
        string='Reserved for SO',
    )
    actual_qty = fields.Float(
        compute=_actual_qty,
        store=True,
        string='Actual Quantity',
    )
