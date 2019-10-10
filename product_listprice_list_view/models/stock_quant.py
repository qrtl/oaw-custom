# Copyright 2019 chrono123 & Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    # For filter New Entry 24
    @api.model
    def create(self, vals):
        new_quant = super(StockQuant, self).create(vals)
        new_quant.product_id.product_tmpl_id.sudo().write({'new_entry_date': fields.Datetime.now()})
        return new_quant
