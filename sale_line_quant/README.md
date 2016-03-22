Handling Case Numbers in Various Transactions
=============================================

This module adds Serial/Lot (Case No.) field in various transactions (SO, PO, and Customer/Supplier Invoice) so that necessary business info is kept in each transaction record. (Serial/Lot is key info in every business transaction).

Main functions achieved by this module are as follows:

* Add a serial number field in SO line, which should be passed to delivery order to reserve a quant of the selected serial number
* Selecting a serial number (a quant) in SO should automatically propose the Stock Owner in SO line
* Add serial number field in PO line and invoice line (both customer and supplier).  In case PO is generated from SO (either via ‘Make To Order’ or ‘Buy VCI’ route), PO should get the serial number automatically from SO line
* An invoice should take serial number from the originating document (i.e. serial number in customer invoice should be taken from SO line, and one in supplier invoice should be from PO line)
* When receipt is done with serial number, it should trigger updating PO line, SO line and delivery with the received serial number (in case serial number had been left blank in SO for ‘Make To Order’ case)
* Cost Price in SO line (we select ‘Display margins on sales orders’ in sales configuration) should be taken from selected quant (serial number)
* For consignment scenario, cost price proposal in SO line should reflect the expected amount in purchasing currency
 * Add new fields in quant - 'purchase currency' and 'purchase currency price'
 * Add new fields in stock move - 'purchase currency' and 'purchase currency price'
 * In case incoming picking is created without reference to a PO, 'unit price' should be auto-calculated by converting the 'purchase currency price' into base currency by applying the exchange rate as of the time of receipt. In other words, user should input 'purchase currency' and 'purchase currency price' instead of inputting 'unit price'. 'Purchase currency' and 'purchase currency price' fields do not have to be updated in case receipt is done with PO reference (non-consignment).
 * In SO line, in case a consignment quant ('stock owner' = supplier or 'purchase currency price' exists) is selected, cost price should be calculated by converting the 'purchase currency price' to SO currency using the exchange rates as of sales order date.
* Prevent multiple procurements getting merged into one PO.  SO and PO should be one to one relationship for ‘Make To Order’ and ‘Buy VCI’ cases.
* Add logic to propose Create Invoice (order_policy) in SO from customer (add a field in customer)
* Adjustment on supplier invoice - in case of vendor consignment, the system should propose Product COGS instead of GR/IR Clearing
* Add a boolean field ‘Enforce Qty 1’ in product category.  Apply following rules to products under this category
 * Serial number + product should be unique in serial number master (stock.product.lot)
 * Qty on hand should not exceed 1 for serial number + product
 * In all transactions where serial number appears, qty should always be 1
  * Auto-split lines in transfer screen in the manner that qty 1 is enforced for each line
* For serial number availability in SO line, selection should be limited to the ones that (1) have on-hand qty > 0, and (2) are not reserved by another SO.
* Validation on Stock Owner, Route and Serial Number in SO line
 * In case stock owner is blank, route cannot be left blank (user should select either ‘Buy’ or ‘Make To Order’)
 * Serial number can be left blank in case of ‘Make To Order’.  Otherwise, the field should be mandatory
 * Serial number validity is checked when SO is being confirmed.
* Add a new option 'On Demand (per SO Line)' for 'Create Invoice' field in SO.  In case this option is selected, user should be able to create an invoice any time from SO.  However, user should not be able to process 'Transfer' in outgoing delivery for lines (stock moves) for which payment has yet to be done.
* Disable SO line wizard (which is activated by ‘Vendor Consignment Stock’ module)
 * ‘Stock Owner’ field should show in line tree in SO form view (currently it does not show)
 * ‘Tax’ field should be made invisible.

Installation
============

No installation steps required other than installing the module itself.
The module depends on vendor_consignment_stock module by OCA.

Configuration
=============

* Product Category (Sales > Product Categories & Attributes > Product Categories)
 * Select 'Enforce Qty 1' field for categories for which transaction quantity is enforced to be 1.
* Customer (Sales > Sales > Customers)
 * Set default 'Create Invoice' value that should be proposed in SO.

Usage
=====

The module should achieve following operation scenarios:
* Consignment
* Make to Order
* Normal stock

