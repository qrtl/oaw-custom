# Copyright 2020 Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "MTO Sale Order Lines",
    "category": "Sale",
    "version": "12.0.1.0.0",
    "author": "Quartile Limited, Timeware Ltd",
    "website": "https://www.quartile.co",
    "depends": ["sale", "sale_order_line_quant", "supplier_user_access"],
    "summary": """ Tree views displaying to internal user all MTO.
    Supplier can see MTO lines of SO where they are
    the supplier and where the customer is related to the suppliers company.
     The tree views exclude MTO that are is_shipment=True""",
    "description": """
    """,
    "data": ["views/sale_order_views.xml"],
    "installable": True,
}
