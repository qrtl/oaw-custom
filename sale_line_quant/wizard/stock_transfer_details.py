# # -*- coding: utf-8 -*-
# ##############################################################################
# #
# #    OpenERP, Open Source Management Solution
# #    Copyright (c) Rooms For (Hong Kong) Limited T/A OSCG. All Rights Reserved
# #
# #    This program is free software: you can redistribute it and/or modify
# #    it under the terms of the GNU Affero General Public License as
# #    published by the Free Software Foundation, either version 3 of the
# #    License, or (at your option) any later version.
# #
# #    This program is distributed in the hope that it will be useful,
# #    but WITHOUT ANY WARRANTY; without even the implied warranty of
# #    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# #    GNU Affero General Public License for more details.
# #
# #    You should have received a copy of the GNU Affero General Public License
# #    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# #
# ##############################################################################
# 
# from datetime import datetime
# from openerp import SUPERUSER_ID
# from openerp.osv import fields, osv
# from openerp.tools import  DEFAULT_SERVER_DATETIME_FORMAT
# from openerp.tools.translate import _
# 
# 
# class stock_transfer_details(models.TransientModel):
#     _inherit = 'stock.transfer_details'
#     
#     def default_get(self, cr, uid, fields, context=None):
#         if context is None: context = {}
#         res = super(stock_transfer_details, self).default_get(cr, uid, fields, context=context)
#         picking_ids = context.get('active_ids', [])
#         active_model = context.get('active_model')
# 
#         if not picking_ids or len(picking_ids) != 1:
#             # Partial Picking Processing may only be done for one picking at a time
#             return res
#         assert active_model in ('stock.picking'), 'Bad context propagation'
#         picking_id, = picking_ids
#         picking = self.pool.get('stock.picking').browse(cr, uid, picking_id, context=context)
#         items = []
#         packs = []
#         if not picking.pack_operation_ids:
#             picking.do_prepare_partial()
#         for op in picking.pack_operation_ids:
#             item = {
#                 'packop_id': op.id,
#                 'product_id': op.product_id.id,
#                 'product_uom_id': op.product_uom_id.id,
#                 'quantity': op.product_qty,
#                 'package_id': op.package_id.id,
#                 'lot_id': op.lot_id.id,
#                 'sourceloc_id': op.location_id.id,
#                 'destinationloc_id': op.location_dest_id.id,
#                 'result_package_id': op.result_package_id.id,
#                 'date': op.date, 
#                 'owner_id': op.owner_id.id,
#             }
#             if op.product_id:
#                 items.append(item)
#             elif op.package_id:
#                 packs.append(item)
#         res.update(item_ids=items)
#         res.update(packop_ids=packs)
#         return res
