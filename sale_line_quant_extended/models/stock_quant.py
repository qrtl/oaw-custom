# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


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
