# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import imgkit
import base64
import cStringIO
import time
from lxml import etree

from openerp import models, fields, api, _
from openerp.tools import config
from openerp.http import request
from openerp.exceptions import RedirectWarning


class ExportProductImage(models.TransientModel):
    _name = "export.product.image"

    image_download = fields.Binary(
        string="Download Image",
        readonly=True,
    )
    name = fields.Char(
        string='Download Image',
        help='Save image',
        default="export_product_image.png"
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
            if action.view_id:
                request.session['kanban_view_id'] = action.view_id.id
        return super(ExportProductImage, self).fields_view_get(
            cr, uid, view_id, view_type, context=context, toolbar=toolbar,
            submenu=submenu)

    @api.model
    def default_get(self, fields_list):
        if request and request.session and request.session.get(
                'kanban_view_id', False):
            product_obj = self.env['product.template']
            view_id = self.env['ir.ui.view'].browse(request.session.get(
                'kanban_view_id', False))
            fields = product_obj.fields_view_get(view_id.id, 'form')
            kanban_fields_list = []

            # Retrieve the fields in the Kanban view, skip fields that are
            # with no_export="True"
            for node in etree.XML(fields['arch']).xpath("//li"):
                if node.xpath(".//field") and not node.xpath(".//field")[
                    0].get("no_export", False):
                    field_label = node.text or node.xpath("i")[0].text
                    kanban_fields_list.append({
                        "field_name": node.xpath(".//field")[0].get("name"),
                        "field_label": field_label
                    })

            product_ids = product_obj.browse(self._context.get("active_ids"))

            if all(not product.image for product in product_ids):
                raise RedirectWarning(_('No products have image to export'))
            for product in product_ids:
                if not product.image:
                    product_ids -= product

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
                        str(product_ids[cnt].image))
                    html_str += """<td>%s</td><td nowrap>""" % (product_image)
                    html_str += "[%s] %s<br>" % (
                        str(product_ids[cnt].default_code),
                        str(product_ids[cnt]["name"])
                    )
                    for field in kanban_fields_list:
                        field_label = field['field_label'].encode('utf-8')
                        field_value = product_ids[cnt][field['field_name']]
                        if type(field_value) == bool:
                            html_str += field_label + ": %s<br>" % str(
                                'Yes' if field_value else 'NO')
                        else:
                            html_str += field_label + ": %s<br>" % str(
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
            res = super(ExportProductImage, self).default_get(fields_list)
            stream = cStringIO.StringIO(file(image_local_path).read())
            res.update({
                'image_download': base64.encodestring(stream.getvalue())
            })

            os.remove(html_file_local_path)
            os.remove(image_local_path)

            return res
