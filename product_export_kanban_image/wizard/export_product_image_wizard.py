# -*- coding: utf-8 -*-
# Copyright 2018-2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import imgkit
import base64
import cStringIO
import time
import math
from lxml import etree
from PIL import Image
from fpdf import FPDF

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
    export_type = fields.Selection(
        selection=[
            ('image', 'Image'),
            ('pdf', 'PDF'),
        ],
        string="Export Format",
        default='image'
    )
    image_type = fields.Selection(
        selection=[
            ('jpeg', 'JPEG'),
            ('png', 'PNG'),
        ],
        string="Image Format",
        default='jpeg'
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
                if node.xpath(".//field") and \
                        not node.xpath(".//field")[0].get("no_export", False):
                    field_condition, condition_field_list = \
                        self.get_condition_eval(node.get('t-if'))
                    field_label = "".join(node.itertext()).split(":")[0] + ": "
                    field_label_currency = False
                    field_array = []
                    for field in node.xpath(".//field"):
                        if field.get('name') == 'currency_id':
                            field_label_currency = field.get('name')
                        else:
                            field_array.append(field.get('name'))
                    item = {
                        "field_condition": field_condition,
                        "condition_field_list": condition_field_list,
                        "field_array": field_array,
                        "field_label": field_label,
                        "field_label_currency": field_label_currency
                    }
                    if item not in kanban_fields_list:
                        kanban_fields_list.append(item)

            filtered_list = self.product_export_filter(
                self._context.get("active_ids"))
            product_ids = product_obj.browse(filtered_list)

            if all(not product[image_field] for product in
                   product_ids):
                raise RedirectWarning(_('No products have image to export'))
            for product in product_ids:
                if not product[image_field]:
                    product_ids -= product

            page_limit = self.row * 3
            export_image_page = []
            image_path_list = []
            page = 1
            while product_ids:
                page_product_ids = product_ids[:page_limit]
                image = self.generate_image(page_product_ids,
                                            kanban_fields_list,
                                            image_field,
                                            view_id,
                                            page)
                image_path_list.append(image[1])
                if self.export_type == 'image':
                    export_image_page.append(image[0].id)
                product_ids = product_ids[page_limit:]
                page += 1

            if self.export_type == 'pdf':
                image_list = []
                first_image = Image.open(image_path_list[0])
                for image in image_path_list[1:]:
                    image_list.append(Image.open(image))

                data_dir = config['data_dir']
                timestamp = int(time.time())
                pdf_file_local_path = "%s/product_image_%d_%d.pdf" % (
                    data_dir,
                    timestamp,
                    self.env.user.id
                )

                pdf = FPDF('P', 'mm', 'A4')
                for image_path in image_path_list:
                    pdf.add_page()
                    pdf.image(image_path, w=pdf.w*0.9)
                pdf.output(pdf_file_local_path, "F")
                stream = cStringIO.StringIO(file(pdf_file_local_path).read())
                pdf_record = self.env['export.product.image'].create({
                    'name': 'image_export.pdf',
                    'image': base64.encodestring(stream.getvalue())
                })
                export_image_page.append(pdf_record.id)

            for image in image_path_list:
                os.remove(image)

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
                                       int(page_option.split("-")[1]) + 1)
            pages = list(set(pages))
            pages.sort()
            filter_list = []
            for page in pages:
                filter_list += product_list[(page - 1) * self.row * 3:][
                               :self.row * 3]
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
                export_product) / 3) / self.row)

    def generate_image(self, product_ids, kanban_fields_list, image_field,
                       view_id, page):
        rows = len(product_ids) / 3
        # Creating the html from the fields list
        html_str = "<table style='width: 210mm'>"
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
                    # Check the condition of the field
                    if field['field_condition']:
                        for condition_field in field['condition_field_list']:
                            # quote is needed for string fields
                            condition_field_value = product_ids[cnt][
                                condition_field]
                            if not (type(condition_field_value) == float or \
                                    type(condition_field_value) == int):
                                condition_field_value = '\'' + \
                                                        condition_field_value + '\''
                            condition = field['field_condition'].replace(
                                condition_field, str(condition_field_value))

                        if not eval(condition):
                            continue

                    # Label Value
                    field_label = field['field_label'].encode('utf-8')
                    if field['field_label_currency']:
                        field_label = field_label.replace(
                            ':', ' %s:' % str(product_ids[cnt][field[
                                'field_label_currency']].name))

                    # Field Value
                    html_str += field_label
                    for field_name in field['field_array']:
                        field_value = product_ids[cnt][field_name]
                        if 'discount' in field_name:
                            if field_value:
                                html_str += "{:,}".format(field_value, 2) + "%"
                            else:
                                html_str += "N/A"
                        elif type(field_value) == float or type(field_value) \
                                == int:
                            html_str += "{:,}".format(int(field_value)) if \
                                field_value != 0 else "N/A"
                        elif type(field_value) == bool:
                            html_str += "%s" % str('Yes' if field_value else 'NO')
                        else:
                            html_str += "%s" % str(field_value)
                        html_str += " "
                    html_str += "<br>"

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
        image_local_path = "%s/product_image_%d_%d.%s" % (
            data_dir,
            timestamp,
            self.env.user.id,
            self.image_type
        )

        Html_file = open(html_file_local_path, "w")
        Html_file.write(html_str)
        Html_file.close()

        image = imgkit.from_file(html_file_local_path, image_local_path,
                                 options={'encoding': "UTF-8"})
        stream = cStringIO.StringIO(file(image_local_path).read())
        image_record = self.env['export.product.image'].create({
            'name': 'page_%d.%s' % (page, self.image_type),
            'image': base64.encodestring(stream.getvalue())
        })

        os.remove(html_file_local_path)
        return image_record, image_local_path

    def get_condition_eval(self, condition_string):
        if condition_string:
            eval_string = ''
            field_list = []
            for part in condition_string.split(' '):
                if 'record' in part:
                    field = part.replace('record.', '').replace(
                        '.raw_value', '')
                    eval_string += field
                    field_list.append(field)
                else:
                    eval_string += part
            return eval_string, field_list
        else:
            return False, False
