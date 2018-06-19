# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import imgkit
import base64
import cStringIO
import time

from openerp import models, fields, api, _
from openerp.tools import config
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

    @api.model
    def default_get(self, fields_list):
        product_obj = self.env['product.template']
        product_ids = product_obj.browse(self._context.get("active_ids"))

        if all(not product.image for product in product_ids):
            raise RedirectWarning(_('No products have image to export'))
        for product in product_ids:
            if not product.image:
                product_ids -= product

        rows = len(product_ids) / 3

        html_str = "<table style='width:100%'>"
        cnt = 0
        for row in range(0, rows + 1):
            html_str = html_str + "<tr>"
            for col in range(0, 3):
                if len(product_ids.ids) == cnt:
                    break
                product_image = '<img src="data:image/*;base64,%s" width="150"/>' % (
                    str(product_ids[cnt].image))
                html_str += """<td>%s</td>
                               <td nowrap>
                                    Name: %s<br>
                                    Price: %.2f
                               </td>""" % \
                            (product_image, product_ids[cnt].name,
                             product_ids[cnt].list_price)
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

        image = imgkit.from_file(html_file_local_path, image_local_path)
        res = super(ExportProductImage, self).default_get(fields_list)
        stream = cStringIO.StringIO(file(image_local_path).read())
        res.update({'image_download': base64.encodestring(stream.getvalue())})

        os.remove(html_file_local_path)
        os.remove(image_local_path)
        return res
