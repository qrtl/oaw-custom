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
        FROM (
            SELECT
                aml2.reconcile_id AS reconcile_id,
                string_agg(ai.number, ',') AS invoice_ref
            FROM
                account_move_line aml2,
                account_move am,
                account_invoice ai,
                account_journal aj
            WHERE
                aml2.move_id = am.id AND
                am.id = ai.move_id AND
                aml2.reconcile_id IS NOT NULL AND
                aj.id = aml2.journal_id AND
                aj.type <> 'situation'
            GROUP BY
                aml2.reconcile_id
        ) AS subquery
        WHERE
            aml1.reconcile_id = subquery.reconcile_id
    '''
    cr.execute(sql)

    # update reconcile_order
    sql = '''
        UPDATE
            account_move_line aml1
        SET
            reconcile_order = subquery.order_ref
        FROM (
            SELECT
                order_query.reconcile_id AS reconcile_id,
                string_agg(order_query.order_number, ',') AS order_ref
            FROM (
                SELECT
                    aml2.reconcile_id as reconcile_id,
                    so.name as order_number
                FROM
                    account_move_line aml2,
                    account_move am,
                    account_invoice ai,
                    account_journal aj,
                    account_invoice_line ail,
                    sale_order so
                WHERE
                    aml2.move_id = am.id AND
                    ail.invoice_id = ai.id AND
                    ail.so_id = so.id AND
                    am.id = ai.move_id AND
                    aml2.reconcile_id IS NOT NULL AND
                    aj.id = aml2.journal_id AND
                    aj.type <> 'situation'
                GROUP BY
                    aml2.reconcile_id,
                    so.name
            ) AS order_query
            GROUP BY order_query.reconcile_id
        ) AS subquery
        WHERE
            aml1.reconcile_id = subquery.reconcile_id
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
                aml2.reconcile_id AS reconcile_id,
                string_agg(am.name, ',') AS item_ref
            FROM
                account_move_line aml2
            LEFT JOIN account_move am ON (aml2.move_id = am.id)
            LEFT JOIN account_journal aj ON (aj.id = aml2.journal_id)
            LEFT JOIN account_invoice ai ON (am.id = ai.move_id)
            WHERE
                aml2.reconcile_id IS NOT NULL AND
                aj.type <> 'situation' AND
                ai.id is null
            GROUP BY aml2.reconcile_id
        ) AS subquery
        WHERE
            am.id = aml1.move_id AND
            aml1.reconcile_id = subquery.reconcile_id
    '''
    cr.execute(sql)

    # update reconcile_invoice (partial reconcile items)
    sql = '''
        UPDATE
            account_move_line aml1
        SET
            reconcile_invoice = subquery.invoice_ref
        FROM (
            SELECT
                aml2.reconcile_partial_id AS reconcile_partial_id,
                string_agg(ai.number, ',') AS invoice_ref
            FROM
                account_move_line aml2,
                account_move am,
                account_invoice ai,
                account_journal aj
            WHERE
                aml2.move_id = am.id AND
                am.id = ai.move_id AND
                aml2.reconcile_partial_id IS NOT NULL AND
                aj.id = aml2.journal_id AND
                aj.type <> 'situation'
            GROUP BY
                aml2.reconcile_partial_id
        ) AS subquery
        WHERE
            aml1.reconcile_partial_id = subquery.reconcile_partial_id
    '''
    cr.execute(sql)

    # update reconcile_order (partial reconcile items)
    sql = '''
        UPDATE
            account_move_line aml1
        SET
            reconcile_order = subquery.order_ref
        FROM (
            SELECT
                order_query.reconcile_partial_id AS reconcile_partial_id,
                string_agg(order_query.order_number, ',') AS order_ref
            FROM (
                SELECT
                    aml2.reconcile_partial_id as reconcile_partial_id,
                    so.name as order_number
                FROM
                    account_move_line aml2,
                    account_move am,
                    account_invoice ai,
                    account_journal aj,
                    account_invoice_line ail,
                    sale_order so
                WHERE
                    aml2.move_id = am.id AND
                    ail.invoice_id = ai.id AND
                    ail.so_id = so.id AND
                    am.id = ai.move_id AND
                    aml2.reconcile_partial_id IS NOT NULL AND
                    aj.id = aml2.journal_id AND
                    aj.type <> 'situation'
                GROUP BY
                    aml2.reconcile_partial_id,
                    so.name
            ) AS order_query
            GROUP BY order_query.reconcile_partial_id
        ) AS subquery
        WHERE
            aml1.reconcile_partial_id = subquery.reconcile_partial_id
    '''
    cr.execute(sql)

    # update reconcile_items (partial reconcile items)
    sql = '''
        UPDATE
            account_move_line aml1
        SET
            reconcile_item = REPLACE(REPLACE(subquery.item_ref, am.name || ',', ''), ',' || am.name, '')
        FROM account_move am,
        (
            SELECT
                aml2.reconcile_partial_id AS reconcile_partial_id,
                string_agg(am.name, ',') AS item_ref
            FROM
                account_move_line aml2
            LEFT JOIN account_move am ON (aml2.move_id = am.id)
            LEFT JOIN account_journal aj ON (aj.id = aml2.journal_id)
            LEFT JOIN account_invoice ai ON (am.id = ai.move_id)
            WHERE
                aml2.reconcile_partial_id IS NOT NULL AND
                aj.type <> 'situation' AND
                ai.id is null
            GROUP BY aml2.reconcile_partial_id
        ) AS subquery
        WHERE
            am.id = aml1.move_id AND
            aml1.reconcile_partial_id = subquery.reconcile_partial_id
        '''
    cr.execute(sql)
