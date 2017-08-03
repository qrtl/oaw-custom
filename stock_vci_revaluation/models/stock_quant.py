# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def _get_current_rates(self):
        rate_data = []
        recs = self.env['res.currency'].search(
            [('active', '=', True),
             ('id', '!=', self.env.user.company_id.currency_id.id)]
        )
        for rec in recs:
            if rec.rate:
                rate_data.append({'currency_id': rec.id, 'rate': rec.rate})
        return rate_data

    @api.model
    def revaluate_vci_stock(self, quant_ids=[]):
        domain = [('owner_id', '!=', self.env.user.company_id.partner_id.id),
                  ('usage', '=', 'internal'),
                  ('purchase_price_unit', '!=', False)]
        if quant_ids:
            domain.append(('id', 'in', quant_ids))
        rate_data = self._get_current_rates()
        for rate_dict in rate_data:
            domain.append(('currency_id', '=', rate_dict['currency_id']))
            quants = self.search(domain)
            domain.pop()
            for q in quants:
                q.cost = q.purchase_price_unit / rate_dict['rate']
        return True
