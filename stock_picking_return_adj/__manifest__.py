# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Adjustments on Picking Return",
    "version": "12.0.1.0.0",
    "author": "Quartile Limited",
    "website": "https://www.quartile.co",
    "category": "stock",
    "description": """
* Add "Is Returned" to indicate if the picking is being returned.
* Hide the "Return" button when there is already a returned picking.
* Only Inventory Manager can access the "Return" button and "Is Returned" field.
    """,
    "depends": ["stock", "stock_picking_show_return"],
    "data": ["views/stock_picking_views.xml"],
    "installable": True,
}
