# -*- coding: utf-8 -*-
# Copyright 2016 Rooms For (Hong Kong) Limited T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class stock_location(models.Model):
    _inherit = 'stock.location'
    
    is_repair_location = fields.Boolean(
        string='Repair Location',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
