# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


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
                # below part does not work since quant is generated after
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

    def action_assign(self, cr, uid, ids, context=None):
        # NEED TO OVERRIDE COMPLETE METHOD SINCE LOGIC WAS IN BETWEEN THE
        # LINES. SEE #oscg TAG FOR CHANGES DONE ON THIS METHOD.
        """ Checks the product type and accordingly writes the state.
        """

        context = context or {}
        quant_obj = self.pool.get("stock.quant")
        to_assign_moves = []
        main_domain = {}
        todo_moves = []
        operations = set()
        for move in self.browse(cr, uid, ids, context=context):
            if move.state not in ('confirmed', 'waiting', 'assigned'):
                continue
            if move.location_id.usage in ('supplier', 'inventory', 'production'):
                to_assign_moves.append(move.id)
                #in case the move is returned, we want to try to find quants before forcing the assignment
                if not move.origin_returned_move_id:
                    continue
            if move.product_id.type == 'consu':
                to_assign_moves.append(move.id)
                continue
            else:
                todo_moves.append(move)

                #we always keep the quants already assigned and try to find the remaining quantity on quants not assigned only
                main_domain[move.id] = [('reservation_id', '=', False), ('qty', '>', 0)]

                # oscg add
                # this is to prevent reserving quants that are taken by
                # quotations for supplier return outgoing move
                if move.location_dest_id.usage == 'supplier':
                    main_domain[move.id] += [('sale_id', '=', False)]

                #if the move is preceeded, restrict the choice of quants in the ones moved previously in original move
                ancestors = self.find_move_ancestors(cr, uid, move, context=context)
                if move.state == 'waiting' and not ancestors:
                    #if the waiting move hasn't yet any ancestor (PO/MO not confirmed yet), don't find any quant available in stock
                    main_domain[move.id] += [('id', '=', False)]
                elif ancestors:
                    main_domain[move.id] += [('history_ids', 'in', ancestors)]

                #if the move is returned from another, restrict the choice of quants to the ones that follow the returned move
                if move.origin_returned_move_id:
                    main_domain[move.id] += [('history_ids', 'in', move.origin_returned_move_id.id)]
                for link in move.linked_move_operation_ids:
                    operations.add(link.operation_id)
        # Check all ops and sort them: we want to process first the packages, then operations with lot then the rest
        operations = list(operations)
        operations.sort(key=lambda x: ((x.package_id and not x.product_id) and -4 or 0) + (x.package_id and -2 or 0) + (x.lot_id and -1 or 0))
        for ops in operations:
            #first try to find quants based on specific domains given by linked operations
            for record in ops.linked_move_operation_ids:
                move = record.move_id
                if move.id in main_domain:
                    domain = main_domain[move.id] + self.pool.get('stock.move.operation.link').get_specific_domain(cr, uid, record, context=context)
                    qty = record.qty
                    if qty:
                    # add a serial number field in SO line, which should be passed to delivery order
                    # to reserve a quant of the selected serial number
                        if record.move_id.quant_id: #oscg
                            quants = [(record.move_id.quant_id, record.move_id.quant_id.qty)] #oscg
                        else: #oscg
                            quants = quant_obj.quants_get_prefered_domain(cr,
                                uid, ops.location_id, move.product_id, qty,
                                domain=domain, prefered_domain_list=[],
                                restrict_lot_id=move.restrict_lot_id.id,
                                restrict_partner_id=move.restrict_partner_id.\
                                id, context=context) #oscg

                        quant_obj.quants_reserve(cr, uid, quants, move, record, context=context)
        for move in todo_moves:
            if move.linked_move_operation_ids:
                continue
            # then if the move isn't totally assigned, try to find quants without any specific domain
            if move.state != 'assigned':
                qty_already_assigned = move.reserved_availability
                qty = move.product_qty - qty_already_assigned

                # add a serial number field in SO line, which should be passed to delivery order
                # to reserve a quant of the selected serial number
                if move.quant_id: #oscg
                    quants = [(move.quant_id, qty)] #oscg
                else: #oscg
                    quants = quant_obj.quants_get_prefered_domain(cr, uid,
                        move.location_id, move.product_id, qty,
                        domain=main_domain[move.id], prefered_domain_list=[],
                        restrict_lot_id=move.restrict_lot_id.id,
                        restrict_partner_id=move.restrict_partner_id.id,
                        context=context) #oscg
                quant_obj.quants_reserve(cr, uid, quants, move, context=context)

        #force assignation of consumable products and incoming from supplier/inventory/production
        if to_assign_moves:
            self.force_assign(cr, uid, to_assign_moves, context=context)
