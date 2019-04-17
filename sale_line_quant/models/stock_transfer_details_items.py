# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class stock_transfer_details_items(models.TransientModel):
    _inherit = 'stock.transfer_details_items'
    
    purchase_line_id = fields.Many2one('purchase.order.line',string="PO Line")
    sale_line_id = fields.Many2one('sale.order.line',string="SO Line")
    move_dest_id = fields.Many2one('stock.move',string="Destination Move")
