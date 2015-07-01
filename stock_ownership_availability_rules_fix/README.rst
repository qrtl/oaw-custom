Stock Ownership Availability Rules Fix
======================================

This module overrides 'quants_get_prefered_domain' method of
stock_ownership_availability_rules to fix the following issues.

- In case of 'Reverse Transfer', the system fails to capture the owner_id of
the existing quant which should be returned, because of which the reservation
of the quant cannot be done without manually assigning the Owner in the
concerned move record.

Assumptions
-----------

- One `location` and `lot_id` can uniquely identify the quant to be returned.  


Contributors
------------

* Yoshi Tashiro <tashiro@roomsfor.hk>
