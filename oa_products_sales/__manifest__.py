# -*- coding: utf-8 -*-
{
    'name': "products_sales_view",

    'summary': """
      Shows sales for each product. """,
      
    'description': """
        A tree view that shows how successful each product was sold by showing information
        of its completed sales orders.
        Completed and then refunded Sales Orders will not be considered.
        View is accessible through Sales/Products/Product Total Sales. Here we see
        aggregated data for each product.
        With a click on a button of each product line we access Sales Order tree view.
        Here we will see for the given product its completed Sales Order Line (of the
        completed Sales Order)
        This view is grouped by customer.
        
        Two majior problems:
        1.)product template view will not be updated by sale.order.line.write()
        2.)sale.order.line.write() will only  be called when Saving quoation, not when confirming quotation.
        
    """,

    'author': "Chrono123",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Product',
    'version': '12.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ["base",
                "product",
                #"product_local_oversea_stock_info",
                # "decimal_precision",
                 "sale",
                # "sale_stock",
                # "product_offer",
                # "model_security_adjust_oaw"
    ],

    # always loaded
    'data': [
        'views/sale_view.xml',
        'views/product_template.xml',
        "wizards/products_sales_wizard.xml",
    ],
    # only loaded in demonstration mode
    #'post_init_hook': '_update_prod_tmpl_fields',
    'installable': True,
    'demo': [],
}
