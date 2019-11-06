# Copyright 2019 Quartile Limted, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Account View Adjust OAW',
    'author': 'Timeware Ltd.',
    'summary': '',
    'version': '12.0.1.0.0',
    'website': 'https://www.ehanse.de',
    'category': 'Accounting',
    'depends': ["base",
                "sale",
                "account",
                ],
    'description': """
* UI improvements in accounting
    """,
    'data': [
        'views/account_payment_views.xml',
    ],
    'installable': True,
}

