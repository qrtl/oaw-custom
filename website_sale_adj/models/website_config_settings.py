# -*- coding: utf-8 -*-
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class WebsiteConfigSettings(models.Model):
    _inherit = 'website.config.settings'

    about_us = fields.Text(
        related='website_id.about_us',
        string='About Us',
    )
    contact_description = fields.Text(
        related='website_id.contact_description',
        string='Contact Information',
    )
    empty_page_message = fields.Text(
        related='website_id.empty_page_message',
        string='Empty Shop Display Message',
    )
    whatsapp_link = fields.Char(
        related='website_id.whatsapp_link',
        string='Whatsapp Link',
    )
    whatsapp_qr_image = fields.Binary(
        related='website_id.whatsapp_qr_image',
        string='Whatsapp QR Code',
    )
    wechat_link = fields.Char(
        related='website_id.wechat_link',
        string='Wechat Link',
    )
    wechat_qr_image = fields.Binary(
        related='website_id.wechat_qr_image',
        string='Wechat QR Code',
    )
