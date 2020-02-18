# Copyright 2020 Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "quotation_reoprt_adjust",

    'summary': """
        Timeware specific reports""",

    'description': """
        Creates quotation, invoice, move reports for 
        - Chrono123 
        - Timeware 
        - Sino 
        Adds report relevant fields and logic: 
        - partner note 
        - Code (Quoation name and Customer Name
    
        
    """,

    'author': "Timeware Limited",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Reports',
    'version': '12.0.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        "base",
        "sale"
    ],

    # always loaded
    'data': [
        
        'views/quotation_report.xml',
        'views/quotation_report_timeware.xml',
        'views/sale_order_form.xml',
        'views/quotation_report_sino.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
