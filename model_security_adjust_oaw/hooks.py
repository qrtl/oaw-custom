# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def _update_partner_offer_fields(cr, registry):

    # Duplicates of one owner
    cr.execute('''
        UPDATE
          supplier_stock
        SET
          owners_duplicates = True
        FROM
            (
            SELECT count(id) COUNT, product_id, partner_id
            FROM supplier_stock
            GROUP BY product_id, partner_id
            ) AS have_duplicates
        WHERE
          supplier_stock.product_id = have_duplicates.product_id
          AND supplier_stock.partner_id = have_duplicates.partner_id
          AND have_duplicates.COUNT > 1
    ''')

    # Update Brand field
    cr.execute('''
        UPDATE
            supplier_stock ss
        SET
            prod_cat_selection = subquery.prod_cat_id
        FROM(
            SELECT pp.id AS product_id, pc.id AS prod_cat_id
            FROM product_category pc
            JOIN product_template pt ON pc.id = pt.categ_id
            JOIN product_product pp ON pt.id = pp.product_tmpl_id
        ) AS subquery
        WHERE
            subquery.product_id = ss.product_id
    ''')

    # Initialize of quant_owner_related_user_id in stock.move
    cr.execute('''
        UPDATE
            stock_move sm
        SET
            quant_owner_related_user_id = subquery.user_id
        FROM(
            SELECT
                sq.id AS quant_id,
                ru.id AS user_id
            FROM stock_quant sq
            JOIN res_partner rp ON rp.id = sq.original_owner_id
            JOIN res_users ru ON rp.id = ru.partner_id
        ) AS subquery
        WHERE
            subquery.quant_id = sm.quant_id
    ''')

