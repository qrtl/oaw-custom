# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import werkzeug

from openerp.http import request
from openerp import http
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.addons.website.models.website import slug
from openerp.addons.website_sale.controllers.main import website_sale

PPG = 20  # Products Per Page
PPR = 4  # Products Per Row


class QueryURL(object):
    def __init__(self, path='', **args):
        self.path = path
        self.args = args

    def __call__(self, path=None, **kw):
        if not path:
            path = self.path
        for k, v in self.args.items():
            kw.setdefault(k, v)
        l = []
        for k, v in kw.items():
            if v:
                if isinstance(v, list) or isinstance(v, set):
                    l.append(werkzeug.url_encode([(k, i) for i in v]))
                else:
                    l.append(werkzeug.url_encode([(k, v)]))
        if l:
            path += '?' + '&'.join(l)
        return path


class table_compute(object):
    def __init__(self):
        self.table = {}

    def _check_place(self, posx, posy, sizex, sizey):
        res = True
        for y in range(sizey):
            for x in range(sizex):
                if posx+x >= PPR:
                    res = False
                    break
                row = self.table.setdefault(posy+y, {})
                if row.setdefault(posx+x) is not None:
                    res = False
                    break
            for x in range(PPR):
                self.table[posy+y].setdefault(x, None)
        return res

    def process(self, products):
        # Compute products positions on the grid
        minpos = 0
        index = 0
        maxy = 0
        for p in products:
            x = min(max(p.website_size_x, 1), PPR)
            y = min(max(p.website_size_y, 1), PPR)
            if index >= PPG:
                x = y = 1

            pos = minpos
            while not self._check_place(pos % PPR, pos/PPR, x, y):
                pos += 1
            # if 21st products (index 20) and the last line is full (PPR products in it), break
            # (pos + 1.0) / PPR is the line where the product would be inserted
            # maxy is the number of existing lines
            # + 1.0 is because pos begins at 0, thus pos 20 is actually the 21st block
            # and to force python to not round the division operation
            if index >= PPG and ((pos + 1.0) / PPR) > maxy:
                break

            if x == 1 and y == 1:   # simple heuristic for CPU optimization
                minpos = pos/PPR

            for y2 in range(y):
                for x2 in range(x):
                    self.table[(pos/PPR)+y2][(pos % PPR)+x2] = False
            self.table[pos/PPR][pos % PPR] = {
                'product': p, 'x': x, 'y': y,
                'class': " ".join(map(lambda x: x.html_class or '', p.website_style_ids))
            }
            if index <= PPG:
                maxy = max(maxy, y+(pos/PPR))
            index += 1

        # Format table according to HTML needs
        rows = self.table.items()
        rows.sort()
        rows = map(lambda x: x[1], rows)
        for col in range(len(rows)):
            cols = rows[col].items()
            cols.sort()
            x += len(cols)
            rows[col] = [c for c in map(lambda x: x[1], cols) if c != False]

        return rows

        # TODO keep with input type hidden


class WebsiteSale(website_sale):

    @http.route(['/supplier/product/<model("supplier.stock"):product>'], type='http', auth="public", website=True)
    def supplier_product(self, product, category='', search='', **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        category_obj = pool['product.public.category']

        context.update(active_id=product.id)

        if category:
            category = category_obj.browse(
                cr, uid, int(category), context=context)
            category = category if category.exists() else False

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])

        keep = QueryURL('/supplier/%s' % product.partner_id.sudo().website_url, category=category and category.id,
                        search=search, attrib=attrib_list)

        category_ids = category_obj.search(cr, uid, [], context=context)
        category_list = category_obj.name_get(
            cr, uid, category_ids, context=context)
        category_list = sorted(category_list, key=lambda category: category[1])

        values = {
            'search': search,
            'supplier_url': product.partner_id.sudo().website_url,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'keep': keep,
            'category_list': category_list,
            'main_object': product,
            'product': product,
        }
        return request.website.render("website_timecheck_supplier.product", values)

    @http.route([
        '/supplier/<supplier_url>',
        '/supplier/<supplier_url>/page/<int:page>',
        '/supplier/<supplier_url>/category/<model("product.public.category"):category>',
        '/supplier/<supplier_url>/category/<model("product.public.category"):category>/page/<int:page>',
    ], type='http', auth="user", website=True)
    def supplier_shop(self, supplier_url, page=0, category=None, search='', **post):
        cr, uid, context, pool = request.cr, SUPERUSER_ID, request.context, request.registry

        supplier = pool.get('res.partner').search(
            cr, uid, [('website_url', '=', supplier_url)], context=context)
        if not supplier:
            return request.website.render("website.403")
        else:
            supplier = supplier[0]

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])

        domain = self._get_supplier_stock_search_domain(
            search, int(supplier), category, attrib_values)

        keep = QueryURL('/', category=category and int(category),
                        search=search, attrib=attrib_list)

        supplier_stock_obj = pool.get('supplier.stock')

        url = "/supplier/%s" % supplier_url
        product_count = supplier_stock_obj.search_count(
            cr, uid, domain, context=context)
        if search:
            post["search"] = search
        if category:
            category = pool['product.public.category'].browse(
                cr, uid, int(category), context=context)
            url = "/supplier/%s/category/%s" % (supplier_url, slug(category))
        if attrib_list:
            post['attrib'] = attrib_list
        pager = request.website.pager(
            url=url, total=product_count, page=page, step=PPG, scope=7, url_args=post)
        product_ids = supplier_stock_obj.search(
            cr, uid, domain, limit=PPG, offset=pager['offset'], order=self._get_supplier_stock_search_order(post), context=context)
        products = supplier_stock_obj.browse(
            cr, uid, product_ids, context=context)

        categs = products.mapped('product_id').mapped(
            'product_tmpl_id').mapped('public_categ_ids')

        style_obj = pool['product.style']
        style_ids = style_obj.search(cr, uid, [], context=context)
        styles = style_obj.browse(cr, uid, style_ids, context=context)

        attributes_obj = request.registry['product.attribute']
        attributes_ids = attributes_obj.search(cr, uid, [], context=context)
        attributes = attributes_obj.browse(
            cr, uid, attributes_ids, context=context)

        # Update session
        request.session.update({
            'supplier_page': True,
            'all_products': True,
            'new_arrival': False,
            'special_offer': False,
            'all_stock': True,
            'hk_stock': False,
            'oversea_stock': False,
        })

        values = {
            'search': search,
            'category': category,
            'supplier_url': supplier_url,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'products': products,
            'bins': table_compute().process(products),
            'rows': PPR,
            'styles': styles,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'style_in_product': lambda style, product: style.id in [s.id for s in product.website_style_ids],
            'attrib_encode': lambda attribs: werkzeug.url_encode([('attrib', i) for i in attribs]),
        }
        return request.website.render("website_timecheck_supplier.products", values)

    def _get_supplier_stock_search_order(self, post):
        return ''

    def _get_supplier_stock_search_domain(self, search, supplier, category, attrib_values):
        domain = [("quantity", ">", 0), ("partner_id", "=", supplier)]

        if search:
            condition_list = []
            operator_list = []
            for srch in search.split(","):
                condition_list += [
                    ('product_id.name', 'ilike', srch),
                    ('product_id.description', 'ilike', srch),
                    ('product_id.description_sale', 'ilike', srch),
                    ('product_id.default_code', 'ilike', srch)
                ]
            # Add '|' to the operator_list, as the search conditions will be joined with OR but not AND
            condition_list_length = len(condition_list)
            while condition_list_length - 1 > 0:
                operator_list += ['|']
                condition_list_length -= 1
            domain += operator_list + condition_list

        if category:
            domain += [('product_id.public_categ_ids',
                        'child_of', int(category))]

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
                    domain += [('product_id.attribute_line_ids.value_ids', 'in', ids)]
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domain += [('product_id.attribute_line_ids.value_ids', 'in', ids)]

        return domain

    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', **post):
        # Update session
        request.session.update({
            'supplier_page': False,
        })
        return super(WebsiteSale, self).shop(page=page, category=category,
                                             search=search, **post)
