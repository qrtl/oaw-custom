# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def _update_account_move_line(cr, registry):
    # update reconcile_invoice
    sql = '''
        UPDATE
            account_move_line aml1
        SET
            reconcile_invoice = subquery.invoice_ref
        FROM(
            SELECT
                subquery2.reconcile_id AS reconcile_id,
                string_agg(subquery2.number, ',') AS invoice_ref
            FROM(
                SELECT
                    ai.number AS number,
                    CASE WHEN aml2.reconcile_id IS NOT NULL THEN aml2.reconcile_id
                         WHEN aml2.reconcile_partial_id IS NOT NULL THEN aml2.reconcile_partial_id
                    ELSE NULL
                    END AS reconcile_id
                FROM account_move_line aml2
                JOIN account_move am ON (aml2.move_id = am.id)
                JOIN account_invoice ai ON (am.id = ai.move_id)
                JOIN account_journal aj ON (aj.id = aml2.journal_id)
                WHERE
                    (aml2.reconcile_id IS NOT NULL OR aml2.reconcile_partial_id IS NOT NULL)
                    AND aj.type <> 'situation'
            ) AS subquery2
            GROUP BY
                subquery2.reconcile_id
        ) AS subquery
        WHERE
            aml1.reconcile_id = subquery.reconcile_id OR aml1.reconcile_partial_id = subquery.reconcile_id
    '''
    cr.execute(sql)

    # update reconcile_order
    sql = '''
        UPDATE
            account_move_line aml1
        SET
            reconcile_order = order_query.order_ref
        FROM(
            SELECT
                order_query2.reconcile_id AS reconcile_id,
                string_agg(order_query2.order_number, ',') AS order_ref
            FROM(
                SELECT
                    so.name as order_number,
                    CASE WHEN aml2.reconcile_id IS NOT NULL THEN aml2.reconcile_id
                         WHEN aml2.reconcile_partial_id IS NOT NULL THEN aml2.reconcile_partial_id
                    ELSE NULL
                    END AS reconcile_id
                FROM account_move_line aml2
                JOIN account_move am ON (aml2.move_id = am.id)
                JOIN account_invoice ai ON (am.id = ai.move_id)
                JOIN account_journal aj ON (aj.id = aml2.journal_id)
                JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)
                JOIN sale_order so ON (ail.so_id = so.id)
                WHERE
                    (aml2.reconcile_id IS NOT NULL OR aml2.reconcile_partial_id IS NOT NULL)
                    AND aj.type <> 'situation'
                GROUP BY
                    aml2.reconcile_id,
                    aml2.reconcile_partial_id,
                    so.name
            ) AS order_query2
            GROUP BY order_query2.reconcile_id
        ) AS order_query
        WHERE
            aml1.reconcile_id = order_query.reconcile_id
            OR aml1.reconcile_partial_id = order_query.reconcile_id
    '''
    cr.execute(sql)

    # update reconcile_items
    sql = '''
        UPDATE
            account_move_line aml1
        SET
            reconcile_item = REPLACE(REPLACE(subquery.item_ref, am.name || ',', ''), ',' || am.name, '')
        FROM account_move am,
        (
            SELECT
                subquery2.reconcile_id AS reconcile_id,
                string_agg(subquery2.name, ',') AS item_ref
            FROM(
                SELECT
                    am.name AS name,
                    CASE WHEN aml2.reconcile_id IS NOT NULL THEN aml2.reconcile_id
                         WHEN aml2.reconcile_partial_id IS NOT NULL THEN aml2.reconcile_partial_id
                    ELSE NULL
                    END AS reconcile_id
                FROM
                    account_move_line aml2
                    LEFT JOIN account_move am ON (aml2.move_id = am.id)
                    LEFT JOIN account_journal aj ON (aj.id = aml2.journal_id)
                    LEFT JOIN account_invoice ai ON (am.id = ai.move_id)
                    WHERE
                        aml2.reconcile_id IS NOT NULL AND
                        aj.type <> 'situation' AND
                        ai.id is null
            ) AS subquery2
            GROUP BY subquery2.reconcile_id
        ) AS subquery
        WHERE
            am.id = aml1.move_id
            AND (aml1.reconcile_id = subquery.reconcile_id OR aml1.reconcile_partial_id = subquery.reconcile_id)
    '''
    cr.execute(sql)
