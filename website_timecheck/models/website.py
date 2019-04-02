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
            domain.append(
                ('stock_new_arrival', '>=', date)
            )
        if request.session.get('hk_stock'):
            domain.append(
                ('qty_local_stock', '>', 0)
            )
        elif request.session.get('oversea_stock'):
            domain.append(
                ('qty_overseas', '>', 0)
            )
        return domain

