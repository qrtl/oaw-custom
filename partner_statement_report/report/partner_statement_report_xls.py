# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import xlwt
from datetime import datetime

from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell
from openerp.addons.partner_statement_report.report.partner_statement_report \
    import PartnerStatementReport
from openerp.tools.translate import _


_column_sizes = [
    ('period', 12),
    ('date', 12),
    ('ref', 20),
    ('payment_ref', 20),
    ('curr_code', 7),
    ('curr_rate', 15),
    ('curr_amt', 20),
    ('debit', 15),
    ('credit', 15),
    ('cumul_bal', 15),
    ('move', 20),
    ('note',20),
    ('rec', 12),
    ('payment_amt', 20),
    ('payment_curr', 20),
    ('int_note', 20),
]


class partner_statement_report_xls(report_xls):
    column_sizes = [x[1] for x in _column_sizes]

    def generate_xls_report(self, _p, _xs, data, objects, wb):

        ws = wb.add_sheet(_p.report_name[:31])
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0

        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        initial_balance_text = {'initial_balance': _('Computed'),
                                'opening_balance': _('Opening Entries'),
                                False: _('No')}

        # Title
        cell_style = xlwt.easyxf(_xs['xls_title'])
        report_name = ' - '.join([_p.report_name.upper(),
                                 _p.company.partner_id.name,
                                 _p.company.currency_id.name])
        c_specs = [
            ('report_name', 1, 0, 'text', report_name),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style)

        # write empty row to define column sizes
        c_sizes = self.column_sizes
        c_specs = [('empty%s' % i, 1, c_sizes[i], 'text', None)
                   for i in range(0, len(c_sizes))]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, set_column_size=True)

        # Header Table
        nbr_columns = 16
        cell_format = _xs['bold'] + _xs['fill_blue'] + _xs['borders_all']
        cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
        c_specs = [
            ('coa', 2, 0, 'text', _('Chart of Account')),
            ('fy', 2, 0, 'text', _('Fiscal Year')),
            ('df', 3, 0, 'text', _p.filter_form(data) ==
             'filter_date' and _('Dates Filter') or _('Periods Filter')),
            ('af', 3, 0, 'text', _('Accounts Filter')),
            ('tm', 2, 0, 'text', _('Target Moves')),
            ('ib', nbr_columns - 12, 0, 'text', _('Initial Balance')),

        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style_center)

        cell_format = _xs['borders_all']
        cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
        c_specs = [
            ('coa', 2, 0, 'text', _p.chart_account.name),
            ('fy', 2, 0, 'text', _p.fiscalyear.name if _p.fiscalyear else '-'),
        ]
        df = _('From') + ': '
        if _p.filter_form(data) == 'filter_date':
            df += _p.start_date if _p.start_date else u''
        else:
            df += _p.start_period.name if _p.start_period else u''
        df += ' ' + _('To') + ': '
        if _p.filter_form(data) == 'filter_date':
            df += _p.stop_date if _p.stop_date else u''
        else:
            df += _p.stop_period.name if _p.stop_period else u''
        c_specs += [
            ('df', 3, 0, 'text', df),
            ('af', 3, 0, 'text', _('Custom Filter')
             if _p.partner_ids else _p.display_partner_account(data)),
            ('tm', 2, 0, 'text', _p.display_target_move(data)),
            ('ib', nbr_columns - 12, 0, 'text',
             initial_balance_text[_p.initial_balance_mode]),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style_center)
        ws.set_horz_split_pos(row_pos)
        row_pos += 1

        # Account Title Row
        cell_format = _xs['xls_title'] + _xs['bold'] + \
            _xs['fill'] + _xs['borders_all']
        account_cell_style = xlwt.easyxf(cell_format)
        account_cell_style_decimal = xlwt.easyxf(
            cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)

        # Column Title Row
        cell_format = _xs['bold']
        c_title_cell_style = xlwt.easyxf(cell_format)

        # Column Header Row
        cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        c_hdr_cell_style = xlwt.easyxf(cell_format)

        # Column Initial Balance Row
        cell_format = _xs['italic'] + _xs['borders_all']
        c_init_cell_style = xlwt.easyxf(cell_format)
        c_init_cell_style_decimal = xlwt.easyxf(
            cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)

        # Column Cumulated balance Row
        cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        c_cumul_cell_style = xlwt.easyxf(cell_format)
        c_cumul_cell_style_decimal = xlwt.easyxf(
            cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)

        # Column Partner Row
        cell_format = _xs['bold']
        c_part_cell_style = xlwt.easyxf(cell_format)

        c_specs = [
            ('period', 1, 0, 'text', _('Period'), None, c_hdr_cell_style),
            ('date', 1, 0, 'text', _('Date'), None, c_hdr_cell_style),
            ('ref', 1, 0, 'text', _('Reference'), None, c_hdr_cell_style),
            ('payment_ref', 1, 0, 'text', _('Payment Reference'), None,
             c_hdr_cell_style),
            ('curr_code', 1, 0, 'text', _('Cur'), None, c_hdr_cell_style),
            ('curr_rate', 1, 0, 'text', _('FX Rate'), None, c_hdr_cell_style),
            ('curr_amt', 1, 0, 'text', _('Amount in Currency'), None,
             c_hdr_cell_style),
            ('debit', 1, 0, 'text', _('Debit'), None, c_hdr_cell_style),
            ('credit', 1, 0, 'text', _('Credit'), None, c_hdr_cell_style),
            ('cumul_bal', 1, 0, 'text', _('Balance'), None, c_hdr_cell_style),
            ('move', 1, 0, 'text', _('Notes 1'), None, c_hdr_cell_style),
            ('note', 1, 0, 'text', _('Notes 2'), None, c_hdr_cell_style),
            ('rec', 1, 0, 'text', _('Rec.'), None, c_hdr_cell_style),
            ('payment_amt', 1, 0, 'text', _('Payment Amount'), None,
             c_hdr_cell_style),
            ('payment_curr', 1, 0, 'text', _('Payment Currency'), None,
             c_hdr_cell_style),
            ('int_note', 1, 0, 'text', _('Internal Notes'), None,
             c_hdr_cell_style),
        ]
        c_hdr_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])

        # Set light-grey background color
        light_green = 'pattern: pattern solid, fore_color 42;'

        # cell styles for statement lines
        ll_cell_format = _xs['borders_all']
        ll_cell_style = xlwt.easyxf(ll_cell_format)
        ll_cell_style_grey = xlwt.easyxf(light_green +
                                         _xs['borders_all'])
        ll_cell_style_date = xlwt.easyxf(
            ll_cell_format + _xs['left'],
            num_format_str=report_xls.date_format)
        ll_cell_style_date_grey = xlwt.easyxf(
            ll_cell_format + _xs['left'] + light_green,
            num_format_str=report_xls.date_format)
        ll_cell_style_decimal = xlwt.easyxf(
            ll_cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)
        ll_cell_style_decimal_grey = xlwt.easyxf(
            ll_cell_format + _xs['right'] + light_green,
            num_format_str=report_xls.decimal_format)
        ll_cell_style_currency = xlwt.easyxf(
            ll_cell_format + _xs['right'],
            num_format_str='0.000000')
        ll_cell_style_currency_grey = xlwt.easyxf(
            ll_cell_format + _xs['right'] + light_green,
            num_format_str='0.000000')

        cnt = 0
        partner_account_summary = {}
        for account in objects:
            if _p['statement_lines'].get(account.id, False) or \
                    _p['init_balance'].get(account.id, False):
                if not _p['partners_order'].get(account.id, False):
                    continue
                cnt += 1
                account_total_debit = 0.0
                account_total_credit = 0.0
                account_balance_cumul = 0.0
                account_balance_cumul_curr = 0.0
                c_specs = [
                    ('acc_title', nbr_columns, 0, 'text',
                     ' - '.join([account.code, account.name]), None,
                     account_cell_style),
                ]
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data, c_title_cell_style)
                row_pos += 1

                for partner_name, p_id, p_ref, p_name in \
                        _p['partners_order'][account.id]:

                    total_debit = 0.0
                    total_credit = 0.0
                    cumul_balance = 0.0
                    cumul_balance_curr = 0.0
                    part_cumul_balance = 0.0
                    part_cumul_balance_curr = 0.0
                    rec_code = False
                    cell_style = ll_cell_style
                    cell_style_date = ll_cell_style_date
                    cell_style_decimal = ll_cell_style_decimal
                    cell_style_currency = ll_cell_style_currency
                    c_specs = [
                        ('partner_title', nbr_columns, 0, 'text',
                         partner_name or _('No Partner'), None,
                         c_part_cell_style),
                    ]
                    row_data = self.xls_row_template(
                        c_specs, [x[0] for x in c_specs])
                    row_pos = self.xls_write_row(
                        ws, row_pos, row_data, c_title_cell_style)
                    row_pos = self.xls_write_row(ws, row_pos, c_hdr_data)
                    row_start_partner = row_pos

                    total_debit = _p['init_balance'][account.id].get(
                        p_id, {}).get('debit') or 0.0
                    total_credit = _p['init_balance'][account.id].get(
                        p_id, {}).get('credit') or 0.0
                    init_deposit = _p['init_deposit'][account.id].get(
                        p_id, {}).get('balance') or 0.0
                    end_deposit = _p['end_deposit'][account.id].get(
                        p_id, {}).get('balance') or 0.0

                    init_line = False
                    if _p.initial_balance_mode and \
                            (total_debit or total_credit):
                        init_line = True

                        part_cumul_balance = \
                            _p['init_balance'][account.id].get(
                                p_id, {}).get('init_balance') or 0.0
                        part_cumul_balance_curr = \
                            _p['init_balance'][account.id].get(
                                p_id, {}).get('init_balance_currency') or 0.0

                        cumul_balance += part_cumul_balance
                        cumul_balance_curr += part_cumul_balance_curr

                        debit_cell = rowcol_to_cell(row_pos, 7)
                        credit_cell = rowcol_to_cell(row_pos, 8)
                        init_bal_formula = debit_cell + '-' + credit_cell

                        # Print row 'Initial Balance' by partner
                        c_specs = [('empty%s' % x, 1, 0, 'text', None)
                                   for x in range(6)]
                        c_specs += [
                            ('init_bal', 1, 0, 'text', _('Initial Balance')),
                            ('debit', 1, 0, 'number', total_debit,
                             None, c_init_cell_style_decimal),
                            ('credit', 1, 0, 'number', total_credit,
                             None, c_init_cell_style_decimal),
                            ('cumul_bal', 1, 0, 'number', None,
                             init_bal_formula, c_init_cell_style_decimal),
                            ('depo_bal_t', 1, 0, 'text', _('Deposit Balance')),
                            ('depo_bal', 1, 0, 'number', init_deposit,
                             None, c_init_cell_style_decimal),
                        ]
                        row_data = self.xls_row_template(
                            c_specs, [x[0] for x in c_specs])
                        row_pos = self.xls_write_row(
                            ws, row_pos, row_data, c_init_cell_style)

                    curr_amt = 0.0
                    curr_rate = 0.0
                    for line in _p['statement_lines'][account.id].get(p_id,
                                                                      []):

                        total_debit += line.get('debit') or 0.0
                        total_credit += line.get('credit') or 0.0

                        label_elements = [line.get('lname') or '']
                        if line.get('invoice_number'):
                            label_elements.append(
                                "(%s)" % (line['invoice_number'],))
                        label = ' '.join(label_elements)
                        cumul_balance += line.get('balance') or 0.0

                        if init_line or row_pos > row_start_partner:
                            cumbal_formula = rowcol_to_cell(
                                row_pos - 1, 9) + '+'
                        else:
                            cumbal_formula = ''
                        debit_cell = rowcol_to_cell(row_pos, 7)
                        credit_cell = rowcol_to_cell(row_pos, 8)
                        cumbal_formula += debit_cell + '-' + credit_cell

                        # Currency Information
                        if not line.get('amount_currency'):
                            curr_rate = 1.000000
                            curr_amt = line.get('debit') + line.get('credit')
                        else:
                            curr_rate = abs(line.get('amount_currency')
                                                   / (line.get('debit') +
                                                      line.get('credit')))
                            curr_amt = abs(line.get('amount_currency'))

                        # Handle Payment
                        if line.get('payment_amt') and line.get(
                                'payment_amt') <> 0 and line.get(
                                'payment_amt') <> curr_amt:
                            payment_amt = line.get('payment_amt')
                            payment_curr = line.get('payment_curr')
                        else:
                            payment_amt = False
                            payment_curr = False

                        # Define reference and note2 (for payments)
                        reference = ''
                        note = ''
                        if line.get('payment_type'):
                            if line.get('payment_type') == "payment":
                                reference = line.get('supplier_invoice_number')
                            if line.get('payment_type') == "receipt":
                                reference = line.get('order_ref')
                            note = line.get('invoice_ref')

                        # Define reference and note2 (for invoices)
                        if line.get('invoice_type'):
                            if line.get('invoice_type') == "in_invoice":
                                reference = line.get('supplier_invoice_number')
                            else:
                                reference = line.get('quotation_number')
                            note = line.get('invoice_number')

                        if (not note or note == '') and line.get(
                                'reconcile_item_ref'):
                            note = line.get('reconcile_item_ref')

                        # Staggered color for different reconcile number
                        if rec_code:
                            if rec_code <> line.get('rec_name'):
                                rec_code = line.get('rec_name')
                                if cell_style == ll_cell_style_grey:
                                    cell_style = ll_cell_style
                                    cell_style_date = ll_cell_style_date
                                    cell_style_decimal = ll_cell_style_decimal
                                    cell_style_currency = \
                                        ll_cell_style_currency
                                else:
                                    cell_style = ll_cell_style_grey
                                    cell_style_date = ll_cell_style_date_grey
                                    cell_style_decimal = \
                                        ll_cell_style_decimal_grey
                                    cell_style_currency = \
                                        ll_cell_style_currency_grey
                        else:
                            rec_code = line.get('rec_name')

                        # Print row statement line data #
                        c_specs = [
                            ('period', 1, 0, 'text', line.get('period_code')
                             or '')
                        ]
                        if line.get('ldate'):
                            c_specs += [
                                ('ldate', 1, 0, 'date', datetime.strptime(
                                    line['ldate'], '%Y-%m-%d'), None,
                                 cell_style_date),
                            ]
                        else:
                            c_specs += [
                                ('ldate', 1, 0, 'text', None),
                            ]
                        c_specs += [
                            ('ref', 1, 0, 'text', reference, None),
                            ('payment_ref', 1, 0, 'text', line.get(
                                'payment_ref')),
                            ('curr_code', 1, 0, 'text', line.get(
                                'currency_code') or
                             _p.company.currency_id.name, None),
                            ('curr_rate', 1, 0, 'number', curr_rate, None,
                             cell_style_currency),
                            ('curr_bal', 1, 0, 'number', curr_amt, None,
                             cell_style_decimal),
                            ('debit', 1, 0, 'number', line.get('debit'),
                             None, cell_style_decimal),
                            ('credit', 1, 0, 'number', line.get('credit'),
                             None, cell_style_decimal),
                            ('cumul_bal', 1, 0, 'number', None,
                             cumbal_formula, cell_style_decimal),
                            ('move', 1, 0, 'text',
                             line.get('move_name') or ''),
                            ('note', 1, 0, 'text', note, None),
                            ('rec_name', 1, 0, 'text',
                             line.get('rec_name') or ''),
                        ]
                        if payment_amt:
                            c_specs += [
                                ('payment_amt', 1, 0, 'number', payment_amt,
                                 None, cell_style_decimal),
                            ]
                        else:
                            c_specs += [
                                ('payment_amt', 1, 0, 'text', None),
                            ]
                        c_specs += [
                            ('payment_curr', 1, 0, 'text', payment_curr or
                             '', None),
                            ('int_note', 1, 0, 'text', line.get(
                                'int_note')),
                        ]
                        row_data = self.xls_row_template(
                            c_specs, [x[0] for x in c_specs])
                        row_pos = self.xls_write_row(
                            ws, row_pos, row_data, cell_style)
                    # end for line

                    # Print row Cumulated Balance by partner #
                    debit_partner_start = rowcol_to_cell(row_start_partner, 7)
                    debit_partner_end = rowcol_to_cell(row_pos - 1, 7)
                    debit_partner_total = 'SUM(' + debit_partner_start + \
                        ':' + debit_partner_end + ')'

                    credit_partner_start = rowcol_to_cell(row_start_partner, 8)
                    credit_partner_end = rowcol_to_cell(row_pos - 1, 8)
                    credit_partner_total = 'SUM(' + credit_partner_start + \
                        ':' + credit_partner_end + ')'

                    bal_partner_debit = rowcol_to_cell(row_pos, 7)
                    bal_partner_credit = rowcol_to_cell(row_pos, 8)
                    bal_partner_total = bal_partner_debit + \
                        '-' + bal_partner_credit

                    c_specs = [('empty%s' % x, 1, 0, 'text', None)
                               for x in range(5)]
                    c_specs += [
                        ('init_bal', 2, 0, 'text',
                         _('Cumulated balance on Partner')),
                        ('debit', 1, 0, 'number', None,
                         debit_partner_total, c_cumul_cell_style_decimal),
                        ('credit', 1, 0, 'number', None,
                         credit_partner_total, c_cumul_cell_style_decimal),
                        ('cumul_bal', 1, 0, 'number', None,
                         bal_partner_total, c_cumul_cell_style_decimal),
                        ('depo_bal_t', 1, 0, 'text', _('Deposit Balance')),
                        ('depo_bal', 1, 0, 'number', end_deposit, None,
                         c_cumul_cell_style_decimal),
                        ('empty%5', 4, 0, 'text', None),
                    ]
                    row_data = self.xls_row_template(
                        c_specs, [x[0] for x in c_specs])
                    row_pos = self.xls_write_row(
                        ws, row_pos, row_data, c_cumul_cell_style)
                    row_pos += 1
                    account_total_debit += total_debit
                    account_total_credit += total_credit
                    account_balance_cumul += cumul_balance
                    account_balance_cumul_curr += cumul_balance_curr

                    # Add the balance to the partner_account_summary
                    if partner_account_summary.get(p_id) and \
                            partner_account_summary[p_id].get(account.type):
                        partner_account_summary[p_id][account.type]['debit'] \
                            += total_debit
                        partner_account_summary[p_id][account.type]['credit'] \
                            += total_credit
                        partner_account_summary[p_id][account.type]['deposit'] \
                            += end_deposit
                    else:
                        if not partner_account_summary.get(p_id):
                            partner_account_summary[p_id] = {
                                account.type: {
                                    'debit': total_debit or 0.0,
                                    'credit': total_credit or 0.0,
                                    'deposit': end_deposit or 0.0
                                }
                            }
                            partner_account_summary[p_id]['partner_name'] = \
                                partner_name
                        else:
                            partner_account_summary[p_id].update({
                                account.type: {
                                    'debit': total_debit or 0.0,
                                    'credit': total_credit or 0.0,
                                    'deposit': end_deposit or 0.0
                                }
                            })

                #  Print row Cumulated Balance by account #
                c_specs = [
                    ('acc_title', 5, 0, 'text', ' - '.
                     join([account.code, account.name])), ]
                c_specs += [
                    ('label', 2, 0, 'text', _('Cumulated balance on Account')),
                    ('debit', 1, 0, 'number', account_total_debit,
                     None, account_cell_style_decimal),
                    ('credit', 1, 0, 'number', account_total_credit,
                     None, account_cell_style_decimal),
                    ('cumul_bal', 1, 0, 'number', account_balance_cumul,
                     None, account_cell_style_decimal),
                    ('empty', 6, 0, 'text', None)
                ]
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data, account_cell_style)
                row_pos += 2

        self.generate_summary_sheet(_p, _xs, wb, partner_account_summary)

    def generate_summary_sheet(self, _p, _xs, wb, partner_account_summary):
        column_sizes = [
            ('partner', 30, 'Partner'),
            ('rec_debit', 15, 'Debit'),
            ('rec_credit', 15, 'Credit'),
            ('rec_balance', 15, 'Balance'),
            ('rec_deposit_balance', 15, 'Deposit Balance'),
            ('pay_debit', 15, 'Debit'),
            ('pay_credit', 15, 'Credit'),
            ('pay_balance', 15, 'Balance'),
            ('pay_deposit_balance', 15, 'Deposit Balance'),
        ]
        column_sizes_list = [x[1] for x in column_sizes]

        ws = wb.add_sheet('Partner Cross Accounts Balances')
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0

        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        # Title
        title_cell_style = xlwt.easyxf(_xs['xls_title'])
        c_title_cell_style = xlwt.easyxf(_xs['bold'])
        c_title_cell_style_center = xlwt.easyxf(_xs['bold'] + _xs['center'])
        account_cell_style = xlwt.easyxf(_xs['xls_title'] + _xs['bold'] + \
            _xs['fill'] + _xs['borders_all'])
        c_hdr_cell_style = xlwt.easyxf(_xs['bold'] + _xs['fill'] + _xs[
            'borders_all'])
        ll_cell_style = xlwt.easyxf(_xs['borders_all'])
        ll_cell_style_decimal = xlwt.easyxf(_xs['borders_all'] + _xs['right'],
            num_format_str=report_xls.decimal_format)

        report_name = ' - '.join([_p.report_name.upper(),
                                  _p.company.partner_id.name,
                                  _p.company.currency_id.name])
        c_specs = [
            ('report_name', 1, 0, 'text', report_name),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=title_cell_style)

        c_sizes = column_sizes_list
        c_specs = [('empty%s' % i, 1, c_sizes[i], 'text', None)
                   for i in range(0, len(c_sizes))]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, set_column_size=True)

        # Table Header Rows
        c_specs = [
            ('acc_title', 9, 0, 'text', 'Partner Cross Accounts Balances',
             None, account_cell_style),
        ]
        row_data = self.xls_row_template(
            c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, c_title_cell_style)
        row_pos += 1

        c_specs = [
            ('empty', 1, 0, 'text', None),
            ('rec', 4, 0, 'text', _('Accounts Receivable'), None),
            ('pay', 4, 0, 'text', _('Accounts Payable'), None),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data,
                                     c_title_cell_style_center)
        c_specs = [(column_sizes[i][0], 1, column_sizes[i][1], 'text',
                    column_sizes[i][2]) for i in range(0, len(column_sizes))]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, c_hdr_cell_style)

        for partner_id, account_summary in partner_account_summary.iteritems():
            rec_debit = 0.0
            rec_credit = 0.0
            rec_deposit_balance = 0.0
            rec_balance = 0.0
            pay_debit = 0.0
            pay_credit = 0.0
            pay_deposit_balance = 0.0
            pay_balance = 0.0
            if account_summary.get('receivable'):
                rec_debit = account_summary['receivable'].get('debit') or 0.0
                rec_credit = account_summary['receivable'].get('credit') or 0.0
                rec_deposit_balance = account_summary['receivable'].get(
                    'deposit') or 0.0
                rec_balance = rec_debit - rec_credit
            if account_summary.get('payable'):
                pay_debit = account_summary['payable'].get('debit') or 0.0
                pay_credit = account_summary['payable'].get('credit') or 0.0
                pay_deposit_balance = account_summary['payable'].get(
                    'deposit') or 0.0
                pay_balance = pay_debit - pay_credit
            c_specs = [
                ('partner', 1, 0, 'text', account_summary['partner_name'],
                 None, ll_cell_style),
                ('rec_debit', 1, 0, 'number', rec_debit, None,
                 ll_cell_style_decimal),
                ('rec_credit', 1, 0, 'number', rec_credit, None,
                 ll_cell_style_decimal),
                ('rec_balance', 1, 0, 'number', rec_balance, None,
                 ll_cell_style_decimal),
                ('rec_deposit_balance', 1, 0, 'number', rec_deposit_balance,
                 None, ll_cell_style_decimal),
                ('pay_debit', 1, 0, 'number', pay_debit, None,
                 ll_cell_style_decimal),
                ('pay_credit', 1, 0, 'number', pay_credit, None,
                 ll_cell_style_decimal),
                ('pay_balance', 1, 0, 'number', pay_balance, None,
                 ll_cell_style_decimal),
                ('pay_deposit_balance', 1, 0, 'number', pay_deposit_balance,
                 None, ll_cell_style_decimal),
            ]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data)

        c_specs = [
            ('empty', 9, 0, 'text', None),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, account_cell_style)

partner_statement_report_xls(
    'report.account.account_report_partner_statement_report_xls',
    'account.account',
    parser=PartnerStatementReport
)
