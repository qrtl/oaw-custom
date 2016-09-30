# -*- coding: utf-8 -*-
# Copyright 2016 Rooms For (Hong Kong) Limited T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, _
from openerp.exceptions import Warning


class stock_transfer_details(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.one
    def do_detailed_transfer(self):
        active_ids = self.env.context.get('active_ids', [])
        picking_ids = self.env['stock.picking'].browse(active_ids)
        for picking in picking_ids:
            if not picking._validate_owner():
                raise Warning(_('Please set valid owner!'))
        return super(stock_transfer_details, self).do_detailed_transfer()
