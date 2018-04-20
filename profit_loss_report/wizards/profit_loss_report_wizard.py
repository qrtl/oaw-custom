# -*- coding: utf-8 -*-
# Copyright 2017-2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz
from openerp import api, models, fields


class ProfitLossReportWizard(models.TransientModel):
    _name = "profit.loss.report.wizard"
    _description = 'Profit & Loss Report Wizard'

    from_date = fields.Date(
        required=True,
        string='From Date',
        default=fields.Date.to_string(
            datetime.now() - relativedelta(days=90)),
    )
    to_date = fields.Date(
        required=True,
        string='To Date',
        default=fields.Date.context_today,
    )

    def _inject_out_invoice_data(self, from_date, to_date):
        query = """
        INSERT INTO
            profit_loss_report (
                create_uid,
                create_date,
                product_id,
                categ_id,
                categ_name,
                lot_id,
                date_order,
                user_id,
                sale_order_id,
                invoice_id,
                list_price,
                net_price,
                net_price_currency_id,
                partner_id,
                partner_ref,
                sale_order_note,
                out_move_id,
                out_move_date,
                in_move_id,
                in_move_date,
                in_move_quant_owner_id,
                purchase_order_id,
                supplier_id,
                supplier_ref,
                purchase_currency_id,
                purchase_currency_price,
                purchase_invoice_id,
                purchase_invoice_line_id,
                supplier_invoice_number,
                customer_invoice_type,
                supplier_invoice_type
            )
        WITH
            outgoing_moves AS (
                SELECT DISTINCT ON (sq.lot_id)
                    sm.id,
                    sq.lot_id,
                    sm.date
                FROM
                    stock_move sm
                JOIN
                    stock_location sl ON sm.location_dest_id = sl.id
                JOIN
                    stock_quant_move_rel qmr ON sm.id = qmr.move_id
                JOIN
                    stock_quant sq ON qmr.quant_id = sq.id
                WHERE
                    sl.usage = 'customer' AND
                    sm.state = 'done' AND
                    sm.company_id = %s
                ORDER BY
                    sq.lot_id,
                    sm.date desc
            ),
            incoming_moves AS (
                SELECT DISTINCT ON (sq.lot_id)
                    sm.id,
                    sq.lot_id,
                    sm.date,
                    sm.quant_owner_id
                FROM
                    stock_move sm
                JOIN
                    stock_location sl ON sm.location_id = sl.id
                JOIN
                    stock_quant_move_rel qmr ON sm.id = qmr.move_id
                JOIN
                    stock_quant sq ON qmr.quant_id = sq.id
                WHERE
                    sl.usage = 'supplier' AND
                    sm.state = 'done' AND
                    sm.company_id = %s
                ORDER BY
                    sq.lot_id,
                    sm.date
            ),
            purchase_data AS (
                SELECT DISTINCT ON (pol.lot_id)
                    po.id AS purchase_id,
                    po.partner_id,
                    rp.ref,
                    po.currency_id,
                    pol.id AS purchase_line_id,
                    pol.price_unit,
                    pol.lot_id
                FROM
                    purchase_order_line pol
                JOIN
                    purchase_order po ON pol.order_id = po.id
                JOIN
                    res_partner rp ON po.partner_id = rp.id
                WHERE
                    pol.company_id = %s
                ORDER BY
                    pol.lot_id,
                    po.date_order desc
            ),
            purchase_invoice_data AS (
                SELECT
                    ail.id as purchase_invoice_line_id,
                    ail.purchase_line_id,
                    ai.id AS supplier_invoice_id,
                    ai.supplier_invoice_number,
                    ai.type AS supplier_invoice_type
                FROM
                    account_invoice_line ail
                JOIN
                    account_invoice ai ON ail.invoice_id = ai.id
                WHERE
                    ai.type in ('in_invoice', 'in_refund') AND
                    ai.state != 'cancel' AND
                    ai.company_id = %s
                ORDER BY
                    ail.purchase_line_id,
                    ai.date_invoice
            )
        SELECT
            %s AS create_uid,
            NOW() AS create_date,
            pp.id,
            pc.id,
            pc.name,
            ail.lot_id,
            so.date_order,
            ai.user_id,
            so.id,
            ai.id,
            pt.list_price,
            ail.price_subtotal,
            ai.currency_id,
            so.partner_id,
            rp.ref,
            so.note,
            om.id,
            om.date,
            im.id,
            im.date,
            im.quant_owner_id,
            pd.purchase_id,
            pd.partner_id,
            pd.ref,
            pd.currency_id,
            pd.price_unit,
            pid.supplier_invoice_id,
            pid.purchase_invoice_line_id,
            pid.supplier_invoice_number,
            ai.type,
            pid.supplier_invoice_type
        FROM
            account_invoice_line ail
        JOIN
            account_invoice ai ON ail.invoice_id = ai.id
        JOIN
            product_product pp ON ail.product_id = pp.id
        JOIN
            product_template pt ON pp.product_tmpl_id = pt.id
        JOIN
            product_category pc ON pt.categ_id = pc.id
        JOIN
            res_partner rp ON ai.partner_id = rp.id
        LEFT JOIN
            sale_order so ON ail.so_id = so.id
        LEFT JOIN
            outgoing_moves om ON ail.lot_id = om.lot_id
        LEFT JOIN
            incoming_moves im ON ail.lot_id = im.lot_id
        LEFT JOIN
            purchase_data pd ON ail.lot_id = pd.lot_id
        LEFT JOIN
            purchase_invoice_data pid ON
                pd.purchase_line_id = pid.purchase_line_id
        WHERE
            ai.type in ('out_invoice', 'out_refund') AND
            (ai.type, pid.supplier_invoice_type) NOT IN (('out_refund',
            'in_refund')) AND
            ai.state in ('open', 'paid') AND
            ai.date_invoice >= %s AND
            ai.date_invoice <= %s AND
            ail.company_id = %s
        """
        company_id = self.env.user.company_id.id
        params = (
            company_id,
            company_id,
            company_id,
            company_id,
            self.env.uid,
            from_date,
            to_date,
            company_id
        )
        self.env.cr.execute(query, params)

    def _inject_purchase_data(self, from_date, to_date):
        query = """
        INSERT INTO
            profit_loss_report (
                create_uid,
                create_date,
                product_id,
                categ_id,
                categ_name,
                lot_id,
                date_order,
                user_id,
                sale_order_id,
                invoice_id,
                list_price,
                net_price,
                net_price_currency_id,
                partner_id,
                partner_ref,
                sale_order_note,
                out_move_id,
                out_move_date,
                in_move_id,
                in_move_date,
                in_move_quant_owner_id,
                purchase_order_id,
                supplier_id,
                supplier_ref,
                purchase_currency_id,
                purchase_currency_price,
                purchase_invoice_id,
                purchase_invoice_line_id,
                supplier_invoice_number,
                customer_invoice_type,
                supplier_invoice_type
            )
        WITH
            outgoing_moves AS (
                SELECT DISTINCT ON (sq.lot_id)
                    sm.id,
                    sq.lot_id,
                    sm.date
                FROM
                    stock_move sm
                JOIN
                    stock_location sl ON sm.location_dest_id = sl.id
                JOIN
                    stock_quant_move_rel qmr ON sm.id = qmr.move_id
                JOIN
                    stock_quant sq ON qmr.quant_id = sq.id
                WHERE
                    sl.usage = 'customer' AND
                    sm.state = 'done' AND
                    sm.company_id = %s
                ORDER BY
                    sq.lot_id,
                    sm.date desc
            ),
            incoming_moves AS (
                SELECT DISTINCT ON (sq.lot_id)
                    sm.id,
                    sq.lot_id,
                    sm.date,
                    sm.quant_owner_id
                FROM
                    stock_move sm
                JOIN
                    stock_location sl ON sm.location_id = sl.id
                JOIN
                    stock_quant_move_rel qmr ON sm.id = qmr.move_id
                JOIN
                    stock_quant sq ON qmr.quant_id = sq.id
                WHERE
                    sl.usage = 'supplier' AND
                    sm.state = 'done' AND
                    sm.company_id = %s
                ORDER BY
                    sq.lot_id,
                    sm.date
            ),
            purchase_invoice_data AS (
                SELECT
                    ail.lot_id,
                    ail.purchase_line_id,
                    ail.id AS purchase_invoice_line_id,
                    ai.id AS supplier_invoice_id,
                    ai.supplier_invoice_number,
                    ai.type AS supplier_invoice_type
                FROM
                    account_invoice_line ail
                JOIN
                    account_invoice ai ON ail.invoice_id = ai.id
                WHERE
                    ai.type in ('in_invoice', 'in_refund') AND
                    ai.state != 'cancel' AND
                    ai.company_id = %s
                ORDER BY
                    ail.purchase_line_id,
                    supplier_invoice_type,
                    ai.date_invoice
            ),
            customer_invoice_data AS (
                SELECT
                    ail.lot_id,
                    ai.id AS customer_invoice_id,
                    ai.user_id,
                    ail.price_subtotal,
                    ai.currency_id,
                    ai.type AS customer_invoice_type
                FROM
                    account_invoice_line ail
                JOIN
                    account_invoice ai ON ail.invoice_id = ai.id
                WHERE
                    ai.type in ('out_invoice', 'out_refund') AND
                    ai.state != 'cancel' AND
                    ai.company_id = %s
                ORDER BY
                    ail.lot_id,
                    ai.date_invoice
            )
        SELECT
            %s AS create_uid,
            NOW() AS create_date,
            pp.id,
            pc.id,
            pc.name,
            im.lot_id,
            so.date_order,
            cid.user_id,
            so.id,
            cid.customer_invoice_id,
            pt.list_price,
            cid.price_subtotal,
            cid.currency_id,
            so.partner_id,
            rp.ref,
            so.note,
            om.id,
            om.date,
            im.id,
            im.date,
            im.quant_owner_id,
            po.id,
            po.partner_id,
            rp.ref,
            po.currency_id,
            pol.price_unit,
            pid.supplier_invoice_id,
            pid.purchase_invoice_line_id,
            pid.supplier_invoice_number,
            cid.customer_invoice_type,
            pid.supplier_invoice_type
        FROM
            purchase_order_line pol
        JOIN
            purchase_order po ON pol.order_id = po.id
        JOIN
            product_product pp ON pol.product_id = pp.id
        JOIN
            product_template pt ON pp.product_tmpl_id = pt.id
        JOIN
            product_category pc ON pt.categ_id = pc.id
        JOIN
            res_partner rp ON pol.partner_id = rp.id
        LEFT JOIN
            purchase_invoice_data pid ON
                pol.lot_id = pid.lot_id
        LEFT JOIN
            sale_order_line sol ON pol.lot_id = sol.lot_id
        LEFT JOIN
            sale_order so ON sol.order_id = so.id
        LEFT JOIN
            customer_invoice_data cid ON
                pol.lot_id = cid.lot_id
        LEFT JOIN
            outgoing_moves om ON pol.lot_id = om.lot_id
        LEFT JOIN
            incoming_moves im ON pol.lot_id = im.lot_id
        WHERE
            po.state not in ('draft', 'sent', 'cancel') AND
            po.id not in (
                SELECT DISTINCT purchase_order_id
                FROM profit_loss_report
            ) AND
            po.date_order >= %s AND
            po.date_order <= (TIMESTAMP %s + INTERVAL '1 DAY') AND
            po.company_id = %s
        """
        company_id = self.env.user.company_id.id
        params = (
            company_id,
            company_id,
            company_id,
            company_id,
            self.env.uid,
            from_date,
            to_date,
            company_id
        )
        self.env.cr.execute(query, params)

    @api.multi
    def _update_records(self):
        self.ensure_one()
        ctx = dict(self._context)
        ctx['company_id'] = self.env.user.company_id.id
        recs = self.env['profit.loss.report'].search([])
        for rec in recs:
            if rec.in_move_date:
                rec.in_period_id = self.env['account.period'].with_context(
                    ctx).find(rec.in_move_date)[:1]
            if rec.in_move_quant_owner_id:
                if rec.in_move_quant_owner_id == \
                        self.env.user.company_id.partner_id:
                    rec.stock_type = 'own'
                else:
                    rec.stock_type = 'vci'
            # Handle the purchase price
            if rec.purchase_invoice_line_id:
                invoice_line = rec.purchase_invoice_line_id
                rec.purchase_currency_price = invoice_line.price_unit * \
                                              (1.0 - (invoice_line.discount
                                                      or 0.0) / 100.0)
                rec.purchase_currency_id = invoice_line.invoice_id.currency_id
                if invoice_line.invoice_id.paid_date:
                    rec.exchange_rate = \
                        1 / invoice_line.invoice_id.paid_date_currency_rate
                else:
                    rec.exchange_rate = 1 / invoice_line.rate
            elif not rec.purchase_order_id and rec.stock_type == 'vci':
                rec.supplier_id = rec.in_move_quant_owner_id
                if rec.supplier_id:
                    rec.supplier_ref = rec.in_move_quant_owner_id.ref
                if rec.in_move_id:
                    rec.purchase_order_id = \
                        rec.in_move_id.purchase_line_id.order_id
                    rec.purchase_currency_id = rec.in_move_id.currency_id
                    rec.purchase_currency_price = \
                        rec.in_move_id.purchase_price_unit
            ctx['date'] = rec.out_move_date or rec.invoice_id.date_invoice \
                if rec.stock_type == 'vci' else rec.in_move_date
            comp_currency_id = self.env.user.company_id.currency_id
            if not rec.exchange_rate:
                if rec.purchase_currency_id == comp_currency_id:
                    rec.exchange_rate = 1.0
                elif ctx['date'] and rec.purchase_currency_id:
                    rec.exchange_rate = self.env['res.currency'].with_context(
                        ctx)._get_conversion_rate(rec.purchase_currency_id,
                                                  comp_currency_id)
            # Handle the net price
            net_price_exchange_rate = 1.0
            if rec.net_price_currency_id == comp_currency_id:
                net_price_exchange_rate = 1.0
            elif ctx['date'] and rec.net_price_currency_id:
                net_price_exchange_rate = self.env['res.currency'].with_context(
                    ctx)._get_conversion_rate(rec.net_price_currency_id,
                                              comp_currency_id)
            base_net_price = rec.net_price * net_price_exchange_rate
            rec.purchase_base_price = \
                rec.purchase_currency_price * rec.exchange_rate
            # Calculate the base_profit
            if rec.customer_invoice_type:
                if rec.customer_invoice_type == "out_refund":
                    rec.base_profit = rec.purchase_base_price - base_net_price
                elif rec.customer_invoice_type == "out_invoice":
                    if rec.supplier_invoice_type:
                        if rec.supplier_invoice_type == "in_invoice":
                            rec.base_profit = base_net_price - \
                                              rec.purchase_base_price
                        else:
                            rec.base_profit = 0
            elif rec.supplier_invoice_type:
                rec.base_profit = 0
            else:
                rec.base_profit = base_net_price - rec.purchase_base_price
            if rec.purchase_base_price:
                rec.base_profit_percent = \
                    rec.base_profit / rec.purchase_base_price * 100
            else:
                rec.base_profit_percent = 999.99
            # Handle the display of multi-payments
            rec.payment_information, rec.base_amount = \
                self._get_payment_information(rec.customer_payment_ids)
            # FIXME below 'if' block may be deprecated as necessary
            # Identify the state of the transaction
            if rec.purchase_invoice_id and rec.purchase_invoice_id.state == \
                    'paid':
                rec.supplier_payment_state = 'done'
            else:
                rec.supplier_payment_state = 'to_pay'
            if rec.out_move_id and rec.out_move_id.state == 'done' and \
                    rec.invoice_id:
                if rec.invoice_id.state == 'paid':
                    rec.sale_state = 'done'
                elif rec.invoice_id.residual and rec.customer_payment_ids:
                    rec.sale_state = 'balance'
                else:
                    rec.sale_state = 'open'
            if rec.customer_invoice_type and rec.customer_invoice_type == \
                    "out_refund":
                rec.state = 'out_refund'
            elif rec.customer_invoice_type and rec.customer_invoice_type == \
                    "in_refund":
                rec.state = 'in_refund'
            elif rec.supplier_invoice_type and rec.supplier_invoice_type == \
                    "in_refund":
                rec.state = 'in_refund'
            elif rec.purchase_invoice_id and rec.purchase_invoice_id.state == \
                    'paid' and rec.invoice_id and rec.invoice_id.state == \
                    'paid':
                rec.state = 'sale_purch_done'
            elif rec.purchase_invoice_id and rec.purchase_invoice_id.state \
                    == 'paid':
                rec.state = 'purch_done'
            elif rec.invoice_id and rec.invoice_id.state == 'paid':
                rec.state = 'sale_done'

    def _get_utc_date(self, date_tz):
        tz = pytz.timezone(self.env.user.tz) or pytz.utc
        date = datetime.strptime(date_tz, '%Y-%m-%d')
        date_local = tz.localize(date, is_dst=None)
        return date_local.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")

    def _get_payment_information(self, payment_ids):
        base_amount = 0
        payment_information = ""
        count = 1
        for payment in payment_ids:
            if not payment.journal_id.currency or \
                            payment.journal_id.currency == \
                            payment.company_id.currency_id:
                payment_exchange_rate = 1.0
                payment_currency = payment.company_id.currency_id
                payment_amount = payment.credit
            else:
                payment_currency = payment.journal_id.currency
                payment_exchange_rate = self.env['res.currency.rate'].search([
                    ('currency_id', '=', payment.journal_id.currency.id),
                    ('name', '<=', payment.date),
                ], order='name desc', limit=1).rate or 1.0
                payment_amount = sum(payment.move_id.line_id.mapped(
                    'amount_currency'))
            payment_information += "%d.%s\n%s\n%s %s\n%f\n\n" % (
                count,
                payment.ref,
                payment.date,
                payment_amount,
                payment_currency.name,
                payment_exchange_rate,
            )
            base_amount += payment.credit
            count += 1
        return payment_information, base_amount

    @api.multi
    def action_generate_profit_loss_records(self):
        self.ensure_one()
        self.env.cr.execute("DELETE FROM profit_loss_report")
        self._inject_out_invoice_data(self.from_date, self.to_date)
        from_date = self._get_utc_date(self.from_date)
        to_date = self._get_utc_date(self.to_date)
        self._inject_purchase_data(from_date, to_date)
        self._update_records()
        res = self.env.ref('profit_loss_report.profit_loss_report_action')
        return res.read()[0]
