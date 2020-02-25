# Copyright 2020  Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Sale per product listview",
    'summary': """
      Shows sales for each product. """,
    'description': """
        For each product a tree view that lists all sale order lines and total amount this product has generated.
        Completed Sale Order Lines will be considered only - from the moment the quotation was confirmed (Todo: when is write() triggered)
        Refunded Sales Orders will not be considered.
        The tree view is per default grouped by customer.  
    """,
    'author': "Quartile Limited, Timeware Limited",
    'category': 'Product',
    'version': '12.0.1.0.0',
    'depends': ["base",
                "product",
                 "sale",
    ],
    'data': [
        'views/sale_view.xml',
        'views/product_template.xml',
        "wizards/products_sales_wizard.xml",
    ],
    'installable': True,
}