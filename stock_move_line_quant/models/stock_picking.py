# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id and self.picking_type_id and self.picking_type_id.code == "incoming":
            self.owner_id = self.partner_id
