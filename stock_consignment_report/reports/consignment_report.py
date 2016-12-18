# -*- coding: utf-8 -*-
# Copyright 2016 Rooms For (Hong Kong) Limited T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields, _
from openerp.addons.abstract_report_xlsx.reports import stock_abstract_report_xlsx
from openerp.report import report_sxw


class ConsignmentReport(models.TransientModel):
    """ Here, we just define class fields.
    For methods, go more bottom at this file.

    The class hierarchy is :
    * ConsignmentReport
    ** ConsignmentReportSection
    *** ConsignmentReportQuant
    """

    _name = 'consignment_report'

    # Filters fields, used for data computation
    filter_partner_id = fields.Many2one(comodel_name='res.partner')
    threshold_date= fields.Date()
    current_date = fields.Date(
        default=fields.Date.context_today
    )

    # Data fields, used to browse report data
    section_ids = fields.One2many(
        comodel_name='consignment_report_section',
        inverse_name='report_id'
    )
    quant_ids = fields.One2many(
        comodel_name='consignment_report_quant',
        inverse_name='report_id'
    )


class ConsignmentReportSection(models.TransientModel):

    _name = 'consignment_report_section'
    # _order = 'name ASC'

    report_id = fields.Many2one(
        comodel_name='consignment_report',
        ondelete='cascade',
        index=True
    )
    quant_ids = fields.One2many(
        comodel_name='consignment_report_quant',
        inverse_name='section_id'
    )

    # Data fields, used for report display
    code = fields.Integer()


class ConsignmentReportQuant(models.TransientModel):

    _name = 'consignment_report_quant'

    report_id = fields.Many2one(
        comodel_name='consignment_report',
        ondelete='cascade',
        index=True
    )
    section_id = fields.Many2one(
        comodel_name='consignment_report_section',
        ondelete='cascade',
        index=True
    )

    # Data fields, used to keep link with real object
    quant_id = fields.Many2one(
        'stock.quant',
        index=True
    )
    reservation_id = fields.Many2one(
        'stock.move',
        index=True
    )
    sale_id = fields.Many2one(
        'sale.order'
    )
    lot_id = fields.Many2one(
        'stock.production.lot',
        index=True
    )

    # Data fields, used for report display
    product_code = fields.Char()
    product_name = fields.Char()
    lot = fields.Char()
    currency = fields.Char()
    purchase_price = fields.Float(digits=(16, 2))
    status = fields.Char()
    remark = fields.Char()
    incoming_date = fields.Datetime()
    stock_days = fields.Integer()
    quant_last_updated = fields.Datetime()
    outgoing_date = fields.Datetime()


class ConsignmentReportCompute(models.TransientModel):
    """ Here, we just define methods.
    For class fields, go more top at this file.
    """

    _inherit = 'consignment_report'

    @api.multi
    def print_report(self):
        self.ensure_one()
        self.compute_data_for_report()
        report_name = 'stock_consignment_report.consignment_report'
        return self.env['report'].get_action(records=self,
                                             report_name=report_name)

    def _prepare_report_xlsx(self):
        self.ensure_one()
        return {
            'filter_partner_id': [(6, 0, self.filter_partner_id.id)],
            'threshold_date': self.threshold_date,
        }

    @api.multi
    def compute_data_for_report(self):
        self.ensure_one()
        model = self.env['consignment_report_quant']
        self._create_section_records()
        sections = self.env['consignment_report_section'].search(
            [('report_id', '=', self.id)])
        for section in sections:
            self._inject_quant_values(section)
            self._update_age(model, section)
            if section.code in [1, 2]:
                self._update_invoice_info(section.id, section.code)
            elif section.code == 3:
                self._update_reservation(model, section.id)
            elif section.code == 4:
                self._delete_supplier_loc_quant(model, section.id)
                self._update_remark(model, section.id)
        self.refresh()

    def _create_section_records(self):
        model = self.env['consignment_report_section']
        for i in [1, 2, 3, 4]:
            vals = {
                'report_id': self.id,
                'code': i
            }
            model.create(vals)

    def _inject_quant_values(self, section):
        query_inject_quant = ""
        if section.code in [1, 2]:
            query_inject_quant += """
WITH
    paid_lot AS (
        SELECT
            lot_id, COALESCE(inv_qty, 0.0) - COALESCE(ref_qty, 0.0) AS qty
        FROM (
            SELECT DISTINCT
                l.lot_id, normal.inv_qty, refund.ref_qty
            FROM
                account_invoice_line l
            INNER JOIN
                account_invoice i ON l.invoice_id = i.id
            LEFT JOIN (
                SELECT
                    lot_id, sum(quantity) AS inv_qty
                FROM
                    account_invoice_line l1
                INNER JOIN
                    account_invoice i1 ON l1.invoice_id = i1.id
                WHERE
                    i1.type = 'in_invoice'
                    AND l1.state = 'paid'
                GROUP BY
                    l1.lot_id
            ) normal ON l.lot_id = normal.lot_id
            LEFT JOIN (
                SELECT
                    lot_id, sum(quantity) AS ref_qty
                FROM
                    account_invoice_line l2
                INNER JOIN
                    account_invoice i2 ON l2.invoice_id = i2.id
                WHERE
                    i2.type = 'in_refund'
                    AND l2.state = 'paid'
                GROUP BY
                    l2.lot_id
            ) refund ON l.lot_id = refund.lot_id
            WHERE i.type = 'in_invoice'
        ) normref
        WHERE
            COALESCE(inv_qty, 0.0) - COALESCE(ref_qty, 0.0) > 0.0
    )
            """
        query_inject_quant += """
INSERT INTO
    consignment_report_quant
    (
    report_id,
    section_id,
    create_uid,
    create_date,
    quant_id,
    reservation_id,
    sale_id,
    product_code,
    product_name,
    lot_id,
    lot,
    currency,
    purchase_price,
    status,
    incoming_date,
    quant_last_updated
    )
SELECT
    %s AS report_id,
    %s AS section_id,
    %s AS create_uid,
    NOW() AS create_date,
    q.id,
    q.reservation_id,
    q.sale_id,
    p.default_code,
    p.name_template,
    l.id,
    l.name,
    c.name,
    q.purchase_price_unit,
    %s AS status,
    q.in_date,
    q.write_date
FROM
    stock_quant q
INNER JOIN
    product_product p ON q.product_id = p.id
INNER JOIN
    stock_production_lot l ON q.lot_id = l.id
INNER JOIN
    stock_location loc ON q.location_id = loc.id
INNER JOIN
    res_currency c ON q.currency_id = c.id
        """
        if section.code in [1, 2]:
            query_inject_quant += """
LEFT JOIN
    paid_lot pl ON q.lot_id = pl.lot_id
            """
        query_inject_quant += """
WHERE loc.usage = %s
    AND q.original_owner_id = %s
        """
        if section.code in [1, 2, 4]:
            query_inject_quant += """
    AND q.write_date >= %s
            """
        if section.code == 1:
            query_inject_quant += """
    AND pl.lot_id IS NOT null
            """
        if section.code == 2:
            query_inject_quant += """
    AND pl.lot_id IS null
            """
        status_desc = {
            1: 'Sold & Paid',
            2: 'Sold & NOT Paid',
            3: 'In Stock',
            4: 'Returned'
        }
        loc_usage = {
            1: 'customer',
            2: 'customer',
            3: 'internal',
            4: 'supplier'
        }
        if section.code in [1, 2, 4]:
            query_inject_quant_params = (
                self.id,
                section.id,
                self.env.uid,
                status_desc[section.code],
                loc_usage[section.code],
                section.report_id.filter_partner_id.id,
                section.report_id.threshold_date
            )
        else:
            query_inject_quant_params = (
                self.id,
                section.id,
                self.env.uid,
                status_desc[section.code],
                loc_usage[section.code],
                section.report_id.filter_partner_id.id
            )
        self.env.cr.execute(query_inject_quant, query_inject_quant_params)

    def _update_invoice_info(self, section_id, code):
        query_update_quant = """
UPDATE
    consignment_report_quant q1
SET
    currency = inv_info.curr,
    purchase_price = inv_info.price,
    remark = inv_info.supp_invoice
FROM (
    SELECT
        inv.currency AS curr,
        inv.price_unit AS price,
        inv.supp_invoice,
        q2.section_id,
        inv.lot_id
    FROM
        consignment_report_quant q2
    INNER JOIN (
        SELECT DISTINCT ON (l.lot_id)
            c.name AS currency,
            l.price_unit,
            i.supplier_invoice_number AS supp_invoice,
            l.lot_id
        FROM
            account_invoice_line l
        INNER JOIN
            account_invoice i ON l.invoice_id = i.id
        INNER JOIN
            res_currency c ON i.currency_id = c.id
        WHERE
            i.type = 'in_invoice'
            AND l.state in %s
        ORDER BY
            l.lot_id,
            i.date_invoice DESC,
            l.write_date DESC
    ) inv
        ON q2.lot_id = inv.lot_id
    WHERE
        q2.section_id = %s
) inv_info
WHERE
    q1.section_id = inv_info.section_id
    AND q1.lot_id = inv_info.lot_id
        """
        state_vals = {
            1: ('paid',),
            2: ('draft', 'open'),
        }
        query_update_quant_params = (
            state_vals[code],
            section_id,
        )
        self.env.cr.execute(query_update_quant, query_update_quant_params)

    def _update_age(self, model, section):
        quants = model.search([('section_id', '=', section.id)])
        for quant in quants:
            if section.code == 3:
                out_date = fields.Datetime.now()
            else:
                out_date = False
                if section.code in [1, 2]:
                    usage = 'customer'
                elif section.code == 4:
                    usage = 'supplier'
                locs = self.env['stock.location'].search([
                    ('usage', '=', usage),
                    ('active', '=', True),
                ])
                move = self.env['stock.move'].search([
                    ('quant_lot_id', '=', quant.lot_id.id),
                    ('picking_type_code', '=', 'outgoing'),
                    ('location_dest_id', 'in', [loc.id for loc in locs]),
                    ('state', '=', 'done'),
                ], order='date asc', limit=1)
                if move:
                    out_date = move.date
            quant.write({'outgoing_date': out_date})
            if out_date:
                stock_days = (
                    fields.Datetime.from_string(out_date) - \
                    fields.Datetime.from_string(quant.incoming_date)
                ).days
                quant.write({'stock_days': stock_days})

    def _update_reservation(self, model, section_id):
        quants = model.search([('section_id', '=', section_id)])
        for quant in quants:
            if quant.reservation_id:
                quant.write({
                    'remark': quant.reservation_id.name_get()[0][1]})
            elif quant.sale_id:
                quant.write({'remark': quant.sale_id.name})

    def _delete_supplier_loc_quant(self, model, section_id):
        quants = model.search([('section_id', '=', section_id)])
        for quant in quants:
            find_duplicate = model.search([
                ('section_id', 'in', range(section_id - 3, section_id)),
                ('lot_id', '=', quant.lot_id.id)
            ])
            if find_duplicate:
                quant.unlink()

    def _update_remark(self, model, section_id):
        quants = model.search([('section_id', '=', section_id)])
        move_obj = self.env['stock.move']
        supp_loc_ids = self.env['stock.location'].search([
            ('usage', '=', 'supplier')]).ids
        for quant in quants:
            move = move_obj.search([
                ('quant_lot_id', '=', quant.lot_id.id),
                ('location_dest_id', 'in', supp_loc_ids),
                ('state', '=', 'done'),
            ], order='date desc', limit=1)
            if move and move.picking_id:
                quant.write({'remark': move.picking_id.note})


class PartnerXslx(stock_abstract_report_xlsx.StockAbstractReportXslx):

    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(PartnerXslx, self).__init__(
            name, table, rml, parser, header, store)

    def _get_report_name(self):
        return _('Consignment Report')

    def _get_report_columns(self, report):
        return {
            0: {'header': _('Code'), 'field': 'product_code', 'width': 10},
            1: {'header': _('Reference Name'), 'field': 'product_name',
                'width': 30},
            2: {'header': _('Case No.'), 'field': 'lot', 'width': 15},
            3: {'header': _('Purch Curr'), 'field': 'currency', 'width': 8},
            4: {'header': _('Curr Price'), 'field': 'purchase_price',
                'type': 'amount', 'width': 15},
            5: {'header': _('Status'), 'field': 'status', 'width': 18},
            6: {'header': _('Remark'), 'field': 'remark', 'width': 30},
            7: {'header': _('Incoming Date'), 'field': 'incoming_date',
                'width': 20},
            8: {'header': _('Age'), 'field': 'stock_days',
                'type': 'number', 'width': 8},
            9: {'header': _('Outgoing Date'), 'field': 'outgoing_date',
                'width': 20},
        }

    def _get_report_filters(self, report):
        return [
            [_('Report Date'), report.current_date],
            [_('Partner'),
                _('[%s] %s') % (
                    report.filter_partner_id.ref,
                    report.filter_partner_id.name)],
            [_('Threshold Date'), report.threshold_date],
        ]

    def _get_col_count_filter_name(self):
        return 2

    def _get_col_count_filter_value(self):
        return 2

    def _generate_report_content(self, workbook, report):
        title_vals = {
            1: 'Part 1. Consignment Sold and Paid',
            2: 'Part 2. Consignment Sold and Not Yet Paid',
            3: 'Part 3. Consignment Available Stock',
            4: 'Part 4. Consignment Back to Supplier'
        }
        for section in report.section_ids:
            self.write_array_title(title_vals[section.code])

            if section.code in [1, 2, 4]:
                self.write_array_header()
            # adjust array header
            elif section.code == 3:
                adj_col = {
                    9: _('Current Date'),
                }
                self.write_array_header(adj_col)

            # for section 1, sort by remark, product_name and lot
            if section.code == 1:
                sorted_quants = sorted(
                    section.quant_ids,
                    key=lambda x: (x.remark, x.product_name, x.lot)
                )
            # otherwise, sort by product_name and lot
            else:
                sorted_quants = sorted(
                    section.quant_ids,
                    key=lambda x: (x.product_name, x.lot)
                )
            for quant in sorted_quants:
                self.write_line(quant)

            # Line break
            self.row_pos += 2


PartnerXslx(
    'report.stock_consignment_report.consignment_report',
    'consignment_report',
    parser=report_sxw.rml_parse
)
