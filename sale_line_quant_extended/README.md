Sale Line Quant Extended
========================

This module adds more features on top of `sale_line_quant`.

- For "Make to Order" and "VCI" scenarios, SO line should keep a link to the associated PO.
- SOs, POs, stock moves and pickings should keep indication of whether the transaction is "Make to Order" related or not.
- Adjusts "Invoicing" (order_policy) proposal logic - order_policy should be `line_check` for "Make to Order" SOs.
- Adds field "Walk-in" in SO and Delivery Order to indicate whether the customer has already picked up goods.
- Adds logic to keep the type of order (Make to Order/Stock) and line field requirements consistent (e.g. line quant cannot be selected if "Make to Order" is selected).
- Adds fields "Make to Order" and "Walk-in" in Stock Move and Picking models.
- Adds various fields to Stock Move model (migrated from `stock_move_view_oaw`).
- Adds the function to reserve quants based on quotation/sales order (together with assigned moves)


Installation
============

No installation steps required other than installing the module itself.

The module depends on:
 - sale_line_quant


Configuration
=============

N/A


Usage
=====

N/A
