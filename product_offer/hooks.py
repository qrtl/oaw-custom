# -*- coding: utf-8 -*-
# Copyright 2017 Rooms For (Hong Kong) Limted T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# from openerp import api, SUPERUSER_ID


def _update_prod_tmpl_fields(cr, registry):
    # update qty_local_qtp with QOH first
    sql = '''
    UPDATE
        product_template pt
    SET
        qty_local_atp = subquery.qoh
    FROM (
        SELECT
            pp.product_tmpl_id AS pt_id,
            SUM(sq.qty) AS qoh
        FROM
            stock_quant sq
            JOIN product_product pp ON sq.product_id = pp.id
            JOIN stock_location sl ON sq.location_id = sl.id
        WHERE
            sl.usage = 'internal'
        GROUP BY
            pp.product_tmpl_id
    ) AS subquery
    WHERE pt.id = subquery.pt_id
    '''
    cr.execute(sql)

    # qty_local_atp = QOH + incoming qty
    sql = '''
    UPDATE
        product_template pt
    SET
        qty_local_atp = qty_local_atp + subquery.in_qty
    FROM (
        SELECT
            pp.product_tmpl_id AS pt_id,
            SUM(sm.product_uom_qty) AS in_qty
        FROM
            stock_move sm
            JOIN product_product pp ON sm.product_id = pp.id
        WHERE
            sm.picking_type_code = 'incoming'
            AND state = 'assigned'
        GROUP BY
            pp.product_tmpl_id
    ) AS subquery
    WHERE pt.id = subquery.pt_id
    '''
    cr.execute(sql)

    # update qty_reserved
    sql = '''
    UPDATE
        product_template pt
    SET
        qty_reserved = subquery.qty_rsvd
    FROM (
        SELECT
            pp.product_tmpl_id AS pt_id,
            SUM(sq.qty) AS qty_rsvd
        FROM
            stock_quant sq
            JOIN product_product pp ON sq.product_id = pp.id
        WHERE
            (sq.reservation_id IS NOT null
             OR sq.sale_id IS NOT null)
            AND usage = 'internal'
        GROUP BY
            pp.product_tmpl_id
    ) AS subquery
    WHERE pt.id = subquery.pt_id
    '''
    cr.execute(sql)

    # update qty_overseas
    sql = '''
    UPDATE
        product_template pt
    SET
        qty_overseas = subquery.qty_ovrs
    FROM (
        SELECT
            pp.product_tmpl_id AS pt_id,
            SUM(ss.quantity) AS qty_ovrs
        FROM
            supplier_stock ss
            JOIN product_product pp ON ss.product_id = pp.id
        GROUP BY
            pp.product_tmpl_id
    ) AS subquery
    WHERE pt.id = subquery.pt_id
    '''
    cr.execute(sql)

    # update last_in_date
    sql = '''
    UPDATE
        product_template pt
    SET
        last_in_date = subquery.date
    FROM (
        SELECT DISTINCT ON (pp.product_tmpl_id)
            pp.product_tmpl_id AS pt_id,
            sm.date
        FROM
            stock_move sm
            JOIN product_product pp ON sm.product_id = pp.id
        WHERE
            sm.state = 'done'
            AND sm.code = 'incoming'
        ORDER BY
            pp.product_tmpl_id, sm.date DESC
    ) AS subquery
    WHERE pt.id = subquery.pt_id
    '''
    cr.execute(sql)
