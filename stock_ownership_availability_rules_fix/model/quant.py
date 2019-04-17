# -*- coding: utf-8 -*-
#    Copyright (c) Rooms For (Hong Kong) Limited T/A OSCG
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from odoo import models, api, fields


class Quant(models.Model):
    _inherit = 'stock.quant'


    @api.model
    def quants_get_prefered_domain(self, location, product, qty, domain=None,
                                   prefered_domain_list=None,
                                   restrict_lot_id=False,
                                   restrict_partner_id=False):
        """Enforce the requested owner on quant reservation.

        If no restriction is imposed, enforce the location partner (or the
        company partner) as owner.

        On the other hand, the core stock module uses the requested owner as
        first choice, but then reserves anything else. Also, no restriction
        means we can reserve anything, while we want to reserve only own stock.

        """
        if domain is None:
            domain = []
        if prefered_domain_list is None:
            prefered_domain_list = []

        if not restrict_partner_id:
            """ >>> replacement by oscg """
#             restrict_partner_id = (location.partner_id.id or
#                                    location.company_id.partner_id.id)
            quant_owner_id = 0
            quants = self.quants_get(location, product, qty, domain=domain,
                                     restrict_lot_id=restrict_lot_id,
                                     restrict_partner_id=False, context=None)
            if quants and quants[0][0] != None:
                quant_owner_id = quants[0][0].owner_id.id
            restrict_partner_id = (quant_owner_id or
                                   location.partner_id.id or
                                   location.company_id.partner_id.id)
            """ <<< replacement by oscg """
            
        domain += [
            ('owner_id', '=', restrict_partner_id),
        ]

        return super(Quant, self).quants_get_prefered_domain(
            location, product, qty, domain, prefered_domain_list,
            restrict_lot_id, restrict_partner_id)
