# Copyright 2019 Quartile Limted, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    supplier_sale_price = fields.Char(string="C123 Sale HKD", store=True)
    supplier_cost_price = fields.Char(string="C123 Cost HKD", store=True)
