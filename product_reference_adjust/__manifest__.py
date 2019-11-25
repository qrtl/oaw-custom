# Copyright 2019 Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "Product representation by name and code",
    'summary': """
        Redefines product representation in various views 
    """,
    'description': """
      Field adjusted
        in RFQ \n
        in 'Supplier Invoice', \n
        in 'Stock Moves Ext' behind Product name field, \n
        in 'Invoice Lines' behind Product name field, \n
        in 'Quants' behind Product name field, \n
        in 'Receipts' and 'Internal Transfer' form views, behind Product name \n
        in 'Transfer' pop-up \n
        in 'Profit & Loss Report' behind Reference field \n
    """,
    'author': 'Timeware Limited',
    'category': 'Products',
    'version': '12.0.1.0.0',
    'depends': [
        'account_invoice_line_view_oaw',
        'stock_view_adjust_oaw',
    ],
    'data': [
        "views/purchase_views.xml",
        "views/account_invoice_line_view.xml",
        "views/stock_move_views.xml",
        "views/stock_quant.xml",
    ],
    'installable': True,
}
