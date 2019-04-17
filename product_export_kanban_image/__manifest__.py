# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Export Product Kanban Image',
    'version': '8.0.2.0.0',
    'category' : 'Products',
     'license': "AGPL-3",
    'summary': """This module allow Export image(s) seleted products from list.""",
    'description': """
    - This module allow Export image(s) for seleted products from list
        - Output image will have a kanban-like structure
        - Each row contains 3 product image
        - No any restriction to export number of images
    """,
    'author': 'Quartile Limited',
    'website': 'https://www.quartile.co',
    'depends': [
        'product',
        'supplier_stock',
    ],
    'data':[
        'wizard/export_product_image_view.xml',
        'wizard/export_product_image_wizard_view.xml',
    ],
    'external_dependencies': {
        'python': ['imgkit'],
    },
    'installable' : True,
    'application' : False,
}
