# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import http
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale


class website_sale(website_sale):

    @http.route('/shop/new_arrival', type='http', auth="public", website=True)
    def shop_new_arrival(self):
        request.session.update({
            'new_arrival': True,
            'special_offer': False,
            'all_products': False,
        })
        return request.redirect('/shop')

    @http.route('/shop/special_offer', type='http', auth="public",
                website=True)
    def shop_special_offer(self):
        request.session.update({
            'new_arrival': False,
            'special_offer': True,
            'all_products': False,
        })
        return request.redirect('/shop')

    @http.route('/shop/all_products', type='http', auth="public", website=True)
    def shop_all_products(self):
        request.session.update({
            'new_arrival': False,
            'special_offer': False,
            'all_products': True,
        })
        return request.redirect('/shop')
