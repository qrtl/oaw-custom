# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import openerp
import werkzeug.utils
from openerp.http import request
from openerp import http
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.addons.website.controllers.main import Website
from openerp.addons.web.controllers.main import Home
from openerp.addons.web.controllers.main import ensure_db


class WebsiteSale(website_sale):

    @http.route('/shop/all_products', type='http', auth="public", website=True)
    def shop_all_products(self):
        request.session.update({
            'all_products': True,
            'new_arrival': False,
            'special_offer': False,
            'all_stock': True,
            'hk_stock': False,
            'oversea_stock': False,
        })
        return request.redirect('/shop')

    @http.route('/shop/special_offer', type='http', auth="public",
                website=True)
    def shop_special_offer(self):
        request.session.update({
            'all_products': False,
            'new_arrival': False,
            'special_offer': True,
            'all_stock': True,
            'hk_stock': False,
            'oversea_stock': False,
        })
        return request.redirect('/shop')

    @http.route('/shop/new_arrival', type='http', auth="public", website=True)
    def shop_new_arrival(self):
        request.session.update({
            'all_products': False,
            'new_arrival': True,
            'special_offer': False,
            'all_stock': True,
            'hk_stock': False,
            'oversea_stock': False,
        })
        return request.redirect('/shop')

    @http.route('/shop/all_stock', type='http', auth="public", website=True)
    def shop_all_stock(self):
        request.session.update({
            'all_products': False,
            'new_arrival': False,
            'special_offer': False,
            'all_stock': True,
            'hk_stock': False,
            'oversea_stock': False,
        })
        return request.redirect('/shop')

    @http.route('/shop/hk_stock', type='http', auth="public", website=True)
    def shop_hk_stock(self):
        request.session.update({
            'all_products': False,
            'new_arrival': False,
            'special_offer': False,
            'all_stock': False,
            'hk_stock': True,
            'oversea_stock': False,
        })
        return request.redirect('/shop')

    @http.route('/shop/oversea_stock', type='http', auth="public",
                website=True)
    def shop_oversea_stock(self):
        request.session.update({
            'all_products': False,
            'new_arrival': False,
            'special_offer': False,
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
        request.session['sale_last_order_id'] = sale_order_id
        request.session['sale_order_id'] = None
        if sale_order_id:
            order = request.registry['sale.order'].browse(cr, SUPERUSER_ID,
                                                          sale_order_id,
                                                          context=context)
            order.message_subscribe([order.partner_id.id])
            order.message_unsubscribe_users([request.website.user_id.id])
        else:
            return request.redirect('/shop')
        return request.website.render("website_timecheck.confirmation",
                                      {'order': order})

    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', **post):
        access_check = self.check_timecheck_access()
        if access_check:
            return access_check
        if category:
            request.session.update({
                'all_products': True,
                'new_arrival': False,
                'special_offer': False,
                'all_stock': True,
                'hk_stock': False,
                'oversea_stock': False,
            })
        res = super(WebsiteSale, self).shop(page=page, category=category,
                                            search=search, **post)
        return res

    @http.route(['/shop/product/<model("product.template"):product>'],
                type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        access_check = self.check_timecheck_access()
        if access_check:
            return access_check
        return super(WebsiteSale, self).product(product=product,
                                                category=category,
                                                search=search,
                                                **kwargs)

    @http.route(['/shop/cart'], type='http', auth="public", website=True)
    def cart(self, **post):
        access_check = self.check_timecheck_access()
        if access_check:
            return access_check
        return super(WebsiteSale, self).cart(**post)

    def check_timecheck_access(self):
        user = request.env['res.users'].sudo().browse(request.uid)
        if user.sudo().has_group('model_security_adjust_oaw.group_supplier'):
            base_url = request.env['ir.config_parameter'].get_param(
                'web.base.url')
            redirect = base_url + '/web'
            return http.redirect_with_hash(redirect)
        return False

    def _get_search_order(self, post):
        # Overwrite by QTL
        # OrderBy will be parsed in orm and so no direct sql injection
        # id is added to be sure that order is a unique sort key
        # return 'website_published desc,%s , id desc' % post.get('order', 'website_sequence desc')
        return 'website_published desc, partner_offer_checked desc,' \
               'website_product_seq_date desc, id desc'

    def _get_search_domain(self, search, category, attrib_values):
        domain = request.website.sale_product_domain()

        # >>> QTL Modified
        # if search:
        #     for srch in search.split(" "):
        #         domain += [
        #             '|', '|', '|', ('name', 'ilike', srch), ('description', 'ilike', srch),
        #             ('description_sale', 'ilike', srch), ('product_variant_ids.default_code', 'ilike', srch)]
        if search:
            condition_list = []
            operator_list = []
            for srch in search.split(","):
                condition_list += [
                    ('name', 'ilike', srch), ('description', 'ilike', srch),
                    ('description_sale', 'ilike',
                     srch), ('product_variant_ids.default_code', 'ilike', srch)
                ]
            # Add '|' to the operator_list, as the search conditions will be joined with OR but not AND
            condition_list_length = len(condition_list)
            while condition_list_length - 1 > 0:
                operator_list += ['|']
                condition_list_length -= 1
            domain += operator_list + condition_list
        # <<< QTL Modified

        if category:
            domain += [('public_categ_ids', 'child_of', int(category))]

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domain += [('attribute_line_ids.value_ids', 'in', ids)]
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domain += [('attribute_line_ids.value_ids', 'in', ids)]

        return domain


class Home(Home):

    @http.route('/web/login', type='http', auth="public")
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
                # << QTL ADD
                #    If user belongs to the timecheck group, redirect them
                #    to the "Special Offer" page.
                if user.has_group('website_timecheck.group_timecheck_trial'):
                    base_url = request.env['ir.config_parameter'].get_param(
                        'web.base.url')
                    redirect = base_url + '/shop/special_offer'
                # >> QTL ADD
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


class Website(Website):

    @http.route('/', type='http', auth="public", website=True)
    def index(self, **kw):
        # << QTL Set the homepage as the shop page
        return request.redirect('/shop')
        # page = 'homepage'
        # try:
        #     main_menu = request.registry['ir.model.data'].get_object(request.cr, request.uid, 'website', 'main_menu')
        # except Exception:
        #     pass
        # else:
        #     first_menu = main_menu.child_id and main_menu.child_id[0]
        #     if first_menu:
        #         if first_menu.url and (not (first_menu.url.startswith(('/page/', '/?', '/#')) or (first_menu.url == '/'))):
        #             return request.redirect(first_menu.url)
        #         if first_menu.url and first_menu.url.startswith('/page/'):
        #             return request.registry['ir.http'].reroute(first_menu.url)
        # return self.page(page)
