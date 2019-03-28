# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def _update_discount_fields(cr, registry):



    # Initializing discount fields
    cr.execute('''
        UPDATE
            supplier_stock
        SET
            product_list_price_discount = subquery.discount,
            discount_in_curr = discount_curr

        FROM(
            SELECT id, (1-(price_unit_base/product_list_price))*100 AS discount, (1-(price_unit/retail_in_currency))*100 AS discount_curr
            FROM supplier_stock
            WHERE price_unit_base>0 AND product_list_price>0 AND price_unit>0 AND retail_in_currency>0
        ) AS subquery
        WHERE
            subquery.id = supplier_stock.id
    ''')
