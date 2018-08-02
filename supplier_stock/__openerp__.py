# -*- coding: utf-8 -*-
# Copyright 2017-2018 Quartile Limited
# Copyright 2017 eHanse
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Supplier Stock',
    'category': 'Stock',
    'version': '8.0.2.0.0',
    'author': 'Quartile Limited',
    'website': 'https://www.quartile.co',
    'depends': [
        'purchase',
        'mail',
    ],
    'summary':"""""",
    'description': """
    """,
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/supplier_location_views.xml',
        'views/supplier_stock_views.xml',
    ],
    'post_init_hook': '_update_partner_offer_fields',
    'installable': True,
}
