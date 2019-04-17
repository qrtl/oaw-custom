# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo
import werkzeug.utils
from odoo.http import request
from odoo import http
from odoo.tools.translate import _
from odoo import SUPERUSER_ID
from odoo.addons.website_sale.controllers.main import website_sale
from odoo.addons.web.controllers.main import Home
from odoo.addons.web.controllers.main import ensure_db


class WebsiteSale(website_sale):

    @http.route('/shop/all_products', type='http', auth="public", website=True)
    def shop_all_products(self):
        request.session.update({
            'all_products': True,
            'new_arrival': False,
            'special_offer': False,
        })
        return request.redirect('/shop')

    @http.route('/shop/new_arrival', type='http', auth="public", website=True)
    def shop_new_arrival(self):
        request.session.update({
            'all_products': False,
            'new_arrival': True,
            'special_offer': False,
        })
        return request.redirect('/shop')

    @http.route('/shop/special_offer', type='http', auth="public", website=True)
    def shop_special_offer(self):
        request.session.update({
            'all_products': False,
            'new_arrival': False,
            'special_offer': True,
        })
        return request.redirect('/shop')

    @http.route('/shop/all_stock', type='http', auth="public", website=True)
    def shop_all_stock(self):
        request.session.update({
            'all_stock': True,
            'hk_stock': False,
            'oversea_stock': False,
        })
        return request.redirect('/shop')

    @http.route('/shop/hk_stock', type='http', auth="public", website=True)
    def shop_hk_stock(self):
        request.session.update({
            'all_stock': False,
            'hk_stock': True,
            'oversea_stock': False,
        })
        return request.redirect('/shop')

    @http.route('/shop/oversea_stock', type='http', auth="public",
                website=True)
    def shop_oversea_stock(self):
        request.session.update({
            'all_stock': False,
            'hk_stock': False,
            'oversea_stock': True,
        })
        return request.redirect('/shop')

    @http.route('/cart/update_payment_delivery_info', type='http',
                auth="public", website=True)
    def update_payment_delivery_info(self, **post):
        order = request.website.sale_get_order(context=request.context)
        if not order:
            return request.redirect("/shop")
        vals = {}
        if post.get('payment_method', False):
            vals['payment_method'] = post['payment_method']
        if post.get('payment_desc', False):
            vals['payment_desc'] = post['payment_desc']
        if post.get('picking_date', False):
            vals['picking_date'] = post['picking_date']
        if post.get('other_inquiry', False):
            vals['other_inquiry'] = post['other_inquiry']
        order.sudo().write(vals)
        return request.redirect("/order/submit")

    @http.route(['/order/submit'], type='http', auth="public",
                website=True)
    def order_submit(self):
        cr, uid, context = request.cr, request.uid, request.context

        sale_order_id = request.session.get('sale_order_id')
        if sale_order_id:
            order = request.registry['sale.order'].browse(cr, SUPERUSER_ID,
                                                          sale_order_id,
                                                          context=context)
        else:
            return request.redirect('/shop')
        request.session['sale_order_id'] = None
        return request.website.render("website_timecheck.confirmation",
                                      {'order': order})


class Home(Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        ensure_db()
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = openerp.SUPERUSER_ID

        values = request.params.copy()
        if not redirect:
            redirect = '/web?' + request.httprequest.query_string
        values['redirect'] = redirect

        try:
            values['databases'] = http.db_list()
        except openerp.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            uid = request.session.authenticate(request.session.db,
                                               request.params['login'],
                                               request.params['password'])
            if uid is not False:
                user = request.env['res.users'].browse(uid)
                if user.has_group('website_timecheck.group_timecheck_basic'):
                    base_url = request.env['ir.config_parameter'].get_param(
                        'web.base.url')
                    redirect = base_url + '/shop/special_offer'
                return http.redirect_with_hash(redirect)
            request.uid = old_uid
            values['error'] = _("Wrong login/password")
        if request.env.ref('web.login', False):
            return request.render('web.login', values)
        else:
            # probably not an odoo compatible database
            error = 'Unable to login on database %s' % request.session.db
            return werkzeug.utils.redirect(
                '/web/database/selector?error=%s' % error, 303)
