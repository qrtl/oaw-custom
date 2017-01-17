# -*- coding: utf-8 -*-
# Copyright 2015-2017 Rooms For (Hong Kong) Limted T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp


class stock_quant(osv.osv):
    _inherit = "stock.quant"


    def _actual_qty(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for quant in self.browse(cr, uid, ids, context=context):
            res[quant.id] = quant.qty - quant.sale_reserver_qty
        return res

    def _get_quant_name(self, cr, uid, ids, name, args, context=None):
        return super(stock_quant, self)._get_quant_name(cr, uid, ids, name,
                                                        args, context=context)


    _columns = {
        # make 'name' a stored field for searching purpose in SO line
        'name': fields.function(
            _get_quant_name,
            type='char',
            store={'stock.quant': (
                lambda self, cr, uid, ids, c={}: ids, [], 10)},
            string='Identifier'
        ),
        'usage': fields.related(
            'location_id', 'usage',
            type='char',
            string='Type of Location',
            readonly=True,
            store=True
        ),
        'sale_reserver_qty': fields.related(
            'reservation_id', 'product_uom_qty',
            type='float',
            string='Sale Reserved Quantity',
            readonly=True,
            store=True
        ),
        'actual_qty': fields.function(
            _actual_qty,
            string='Actual Quantity',
            help="It is: Quantity - Sale Reserved Quantity",
            type='float',
            store={'stock.quant': (
                lambda self, cr, uid, ids, c={}: ids, [], 10)},
        ),
        'currency_id': fields.many2one(
            'res.currency',
            string='Purchase Currency',
            required=False,
            readonly=True
        ),
        'purchase_price_unit': fields.float(
            'Purchase Currency Price',
            required=False,
            digits_compute=dp.get_precision('Product Price'),
            readonly=True
        ),
        'original_owner_id': fields.many2one(
            'res.partner',
            string='Original Owner',
            readonly=True,
        )
    }

    def _quant_create(self, cr, uid, qty, move, lot_id=False, owner_id=False,
                      src_package_id=False, dest_package_id=False,
                      force_location_from=False, force_location_to=False,
                      context=None):
        quant = super(stock_quant, self)._quant_create(cr, uid, qty, move,
                                                       lot_id, owner_id,
                                                       src_package_id,
                                                       dest_package_id,
                                                       force_location_from,
                                                       force_location_to,
                                                       context)
        self.write(cr, uid, [quant.id], {
            'currency_id': move.currency_id.id,
            'purchase_price_unit': move.purchase_price_unit,
            'original_owner_id': quant.owner_id.id
        }, context)
        return quant

    # this is to update 'name' field at installation/upgrade
    def init(self, cr):
        quant_ids = self.search(cr, SUPERUSER_ID, [])
        self.write(cr, SUPERUSER_ID, quant_ids, {})
