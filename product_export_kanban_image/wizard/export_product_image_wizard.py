# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import imgkit
import base64
import cStringIO
import time
import math
from lxml import etree

from openerp import models, fields, api, _
from openerp.tools import config
from openerp.http import request
from openerp.exceptions import RedirectWarning
from openerp.exceptions import Warning as UserError


class ExportProductImageWizard(models.TransientModel):
    _name = "export.product.image.wizard"

    row = fields.Integer(
        string='No. of Rows',
        required=True,
        default=16,
    )
    product_limit = fields.Integer(
        string='Export Limit',
    )
    total_page = fields.Integer(
        string='Total No. of Page(s)',
        readonly=True,
    )
    export_pages = fields.Char(
        string='Page(s) to Export',
    )

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        # Check the action_id in the context and store the view_id to the
        # request.session object
        if context.get('params', False) and \
                context.get('params', False).get('action', False):
            action_id = context.get('params', False).get('action', False)
            action = self.pool('ir.actions.act_window').browse(
                cr, uid, action_id, context=context)
            for view in action.view_ids:
                if view.view_mode == 'kanban':
                    request.session['kanban_view_id'] = view.view_id.id
            else:
                if action.view_id:
                    request.session['kanban_view_id'] = action.view_id.id
        return super(ExportProductImageWizard, self).fields_view_get(
            cr, uid, view_id, view_type, context=context, toolbar=toolbar,
            submenu=submenu)

    @api.multi
    def export_product_image(self):
        if request and request.session and request.session.get(
                'kanban_view_id', False):
            view_id = self.env['ir.ui.view'].browse(request.session.get(
                'kanban_view_id', False))
            product_obj = self.env['product.template']
            image_field = 'image'
            if view_id.model == 'supplier.stock':
                product_obj = self.env['supplier.stock']
                image_field = 'image_medium'
            fields = product_obj.sudo().fields_view_get(view_id.id, 'form')
            kanban_fields_list = []

            # Retrieve the fields in the Kanban view, skip fields that are
            # with no_export="True"
            for node in etree.XML(fields['arch']).xpath("//li"):
                if node.xpath(".//field") and not node.xpath(".//field")[
                    0].get("no_export", False):
                    field_label = node.text or node.xpath("i") and \
                                  node.xpath("i")[0].text or node.xpath("b")\
                                  and node.xpath("b")[0].text
                    field_name = node.xpath(".//field")[0].get("name")
                    if ':' not in field_label:
                        field_label = [field_label, node.xpath(".//field")[
                            0].get("name")]
                        field_name = node.xpath(".//field")[1].get("name")
                    item = {
                        "field_name": field_name,
                        "field_label": field_label
                    }
                    if item not in kanban_fields_list:
                        kanban_fields_list.append(item)

            filtered_list = self.product_export_filter(self._context.get("active_ids"))
            product_ids = product_obj.browse(filtered_list)

            if all(not product[image_field] for product in
                   product_ids):
                raise RedirectWarning(_('No products have image to export'))
            for product in product_ids:
                if not product[image_field]:
                    product_ids -= product

            page_limit = self.row*3
            export_image_page = []
            page = 1
            while product_ids:
                page_product_ids = product_ids[:page_limit]
                export_image_page.append(self.generate_image(page_product_ids,
                                                             kanban_fields_list,
                                                             image_field,
                                                             view_id,
                                                             page).id)
                product_ids = product_ids[page_limit:]
                page += 1

            return {
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'export.product.image',
                'domain': str([('id', 'in', export_image_page)]),
                'view_id': self.env.ref(
                    'product_export_kanban_image.export_product_image_view'
                    '').id,
                'type': 'ir.actions.act_window',
                'target': 'new'
            }

    def product_export_filter(self, product_ids):
        product_list = product_ids[:self.product_limit] if \
                        self.product_limit and len(product_ids) > \
                                          self.product_limit else product_ids
        if self.export_pages:
            pages = []
            for page_option in self.export_pages.split(","):
                try:
                    pages.append(int(page_option))
                except ValueError:
                    if len(page_option.split("-")) > 1:
                        pages += range(int(page_option.split("-")[0]),
                                       int(page_option.split("-")[1])+1)
            pages = list(set(pages))
            pages.sort()
            filter_list = []
            for page in pages:
                filter_list += product_list[(page-1)*self.row*3:][:self.row*3]
            product_list = filter_list
        return product_list

    @api.onchange('row', 'product_limit')
    def _onchange_total_page(self):
        export_product = len(self._context.get("active_ids"))
        if self.product_limit and export_product > self.product_limit:
            export_product = self.product_limit
        if self.row <= 0:
            raise UserError(_('No. of row must be greater than 0.'))
        else:
            self.total_page = math.ceil(math.ceil(float(
                export_product)/3)/self.row)

    def generate_image(self, product_ids, kanban_fields_list, image_field,
                       view_id, page):
        rows = len(product_ids) / 3
        # Creating the html from the fields list
        html_str = "<table style='width:100%'>"
        cnt = 0
        for row in range(0, rows + 1):
            html_str = html_str + "<tr>"
            for col in range(0, 3):
                if len(product_ids.ids) == cnt:
                    break
                product_image = '<img src="data:image/*;base64,%s" width="150"/>' % (
                    str(product_ids[cnt][image_field]))
                html_str += """<td>%s</td><td nowrap>""" % (product_image)
                if view_id.model == 'supplier.stock':
                    html_str += "[%s] %s<br>" % (
                        str(product_ids[cnt].product_id.sudo().default_code),
                        str(product_ids[cnt].product_id.sudo().name)
                    )
                else:
                    html_str += "[%s] %s<br>" % (
                        str(product_ids[cnt].default_code),
                        str(product_ids[cnt].name)
                    )
                for field in kanban_fields_list:
                    if isinstance(field['field_label'], list):
                        field_label = '%s %s: ' % (
                            field['field_label'][0].encode('utf-8'),
                            product_ids[cnt][field['field_label'][
                                1]].name.encode('utf-8'),
                        )
                    else:
                        field_label = field['field_label'].encode('utf-8')
                    field_value = product_ids[cnt][field['field_name']]
                    if 'discount' in field['field_name']:
                        if field_value:
                            html_str += field_label + "{:,}".format(
                                field_value, 2) + "%<br>"
                        else:
                            html_str += field_label + "N/A<br>"
                    elif type(field_value) == float or type(field_value) \
                            == int:
                        value = "{:,}".format(int(field_value)) if \
                            field_value != 0 else "N/A"
                        html_str += field_label + value + "<br>"
                    elif type(field_value) == bool:
                        html_str += field_label + " %s<br>" % str(
                            'Yes' if field_value else 'NO')
                    else:
                        html_str += field_label + " %s<br>" % str(
                            field_value)

                html_str += "</td>"
                cnt += 1

            html_str = html_str + "</tr>"
        html_str = html_str + "</table>"

        # Get the data_dir and form the paths for the temporary html and
        # image files with current timestamp
        data_dir = config['data_dir']
        timestamp = int(time.time())
        html_file_local_path = "%s/product_image_%d_%d.html" % (
            data_dir,
            timestamp,
            self.env.user.id
        )
        image_local_path = "%s/product_image_%d_%d.png" % (
            data_dir,
            timestamp,
            self.env.user.id
        )

        Html_file = open(html_file_local_path, "w")
        Html_file.write(html_str)
        Html_file.close()

        image = imgkit.from_file(html_file_local_path, image_local_path,
                                 options={'encoding': "UTF-8"})
        stream = cStringIO.StringIO(file(image_local_path).read())
        image_record = self.env['export.product.image'].create({
            'name': 'page_%d.png' % page,
            'image': base64.encodestring(stream.getvalue())
        })

        os.remove(html_file_local_path)
        os.remove(image_local_path)
        return image_record
