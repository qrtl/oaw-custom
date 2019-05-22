# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    quant_id = fields.Many2one(
        'stock.quant',
        string='Stock Quant',
        copy=False,
    )
    lot_id = fields.Many2one(
        related='quant_id.lot_id',
        string='Case No.',
    )
    stock_owner_id = fields.Many2one(
        related='quant_id.owner_id',
        string='Stock Owner',
    )
    mto = fields.Boolean(
        compute='_compute_route',
        store=True,
        string='Is MTO?',
    )

    @api.multi
    @api.depends('order_id.is_mto')
    def _compute_route(self):
        for line in self:
            model, res_id = self.env['ir.model.data'].get_object_reference(
                'stock', 'route_warehouse0_mto')
            if line.order_id.is_mto:
                line.route_id = res_id
                line.mto = True
                line.quant_id = False
                line.stock_owner_id = False
            else:
                line.route_id = False
                line.mto = False

    @api.onchange('quant_id')
    def _onchange_quant_id(self):
        if self.quant_id:
            self.stock_owner_id = self.quant_id.owner_id
            if self.quant_id.purchase_price_unit > 0:
                self.purchase_price = self.env['res.currency'].compute(
                    self.quant_id.purchase_price_unit,
                    self.quant_id.currency_id)
            else:
                self.purchase_price = self.quant_id.product_id.stock_value /\
                                      self.quant_id.product_id.qty_available

    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        values = super(SaleOrderLine, self)._prepare_procurement_values(
            group_id)
        self.ensure_one()
        values.update({
            'quant_id': self.quant_id.id,
            'lot_id': self.lot_id.id,
        })
        return values

    @api.constrains('product_id', 'quant_id', 'state')
    def _validate_quant(self):
        for rec in self:
            if rec.product_id.tracking in ('serial', 'lot') and not rec.quant_id and \
                    rec.state == 'sale':
                raise ValidationError(_('You must select a quant '
                                        'for products tracking with Serial Number'))
