# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale Line Quant Extended',
    'category': 'Sales',
    'version': '8.0.1.3.0',
    'author': 'Quartile Limited',
    'website': 'https://www.odoo-asia.com',
    'depends': [
        'sale_line_quant',
        'base_action_rule',
    ],
    'summary':"""""",
    'description': """
    """,
    'data': [
        'data/ir_actions.xml',
        'data/base_action_rule_data.xml',
        'data/update.xml',
        'views/sale_view.xml',
        'views/purchase_view.xml',
    ],
    'installable': True,
}
