# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
from openerp import models, fields, api
from openerp.http import request
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class website(models.Model):
    _inherit = 'website'

    def sale_product_domain(self):
        domain = super(website, self).sale_product_domain()
        date = (datetime.datetime.now() + datetime.timedelta(
            days=-7)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        if request.session.get('new_arrival'):
            domain.extend((
                ("qty_overseas", ">", 0),
                ('partner_stock_new_arrival', '>=', date)
            ))
        elif request.session.get('special_offer'):
            domain.extend((
                ("qty_overseas", ">", 0),
                ('partner_stock_special_offer', '>=', date)
            ))
        return domain
