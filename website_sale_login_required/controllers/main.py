# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import http
from openerp.addons.website_sale.controllers.main import website_sale


class WebsiteSale(website_sale):

    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="user", website=True)
    def shop(self, page=0, category=None, search='', **post):
        return super(WebsiteSale, self).shop(page=page, category=category,
                                             search=search, **post)

    @http.route(['/shop/product/<model("product.template"):product>'],
                type='http', auth="user", website=True)
    def product(self, product, category='', search='', **kwargs):
        return super(WebsiteSale, self).product(product=product,
                                                category=category,
                                                search=search,
                                                **kwargs)

    @http.route(['/shop/cart'], type='http', auth="user", website=True)
    def cart(self, **post):
        return super(WebsiteSale, self).cart(**post)
