# -*- coding: utf-8 -*-
# Copyright 2016 Rooms For (Hong Kong) Limited T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields, _
from openerp.addons.abstract_report_xlsx.reports \
    import stock_abstract_report_xlsx
from openerp.report import report_sxw
from datetime import datetime


class OfferReport(models.TransientModel):
    """ Here, we just define class fields.
    For methods, go more bottom at this file.

    The class hierarchy is :
    * ConsignmentReport
    ** ConsignmentReportSection
    *** ConsignmentReportQuant
    """

    _name = 'offer.report'

    new_stock_days = fields.Integer()
    stock_threshold_date = fields.Date()
    sales_threshold_date = fields.Date()
    current_date = fields.Date(
        default=fields.Datetime.to_string(datetime.today())
    )

    # Data fields, used to browse report data
    section_ids = fields.One2many(
        comodel_name='offer.report.section',
        inverse_name='report_id'
    )
    quant_ids = fields.One2many(
        comodel_name='offer.report.line',
        inverse_name='report_id'
    )


class OfferReportSection(models.TransientModel):

    _name = 'offer.report.section'

    report_id = fields.Many2one(
        comodel_name='offer.report',
        ondelete='cascade',
        index=True
    )
    quant_ids = fields.One2many(
        comodel_name='offer.report.line',
        inverse_name='section_id'
    )

    # Data fields, used for report display
    code = fields.Integer()


class OfferReportLine(models.TransientModel):

    _name = 'offer.report.line'

    report_id = fields.Many2one(
        comodel_name='offer.report',
        ondelete='cascade',
        index=True
    )
    section_id = fields.Many2one(
        comodel_name='offer.report.section',
        ondelete='cascade',
        index=True
    )

    # Data fields, used to keep link with real object
    product_id = fields.Many2one(
        'product.product',
        index=True
    )
    quant_id = fields.Many2one(
        'stock.quant',
    )
    owner_id = fields.Many2one(
        'res.partner',
        index=True
    )
    reservation_id = fields.Many2one(
        'stock.move',
    )
    sale_id = fields.Many2one(
        'sale.order'
    )
    lot_id = fields.Many2one(
        'stock.production.lot',
    )

    # Data fields, used for report display
    category_name = fields.Char()
    product_code = fields.Char()
    product_name = fields.Char()
    qty = fields.Integer()
    image_small = fields.Binary()
    list_price = fields.Float()
    margin_percent = fields.Float()
    owner_name = fields.Char()
    unit_cost = fields.Float(digits=(16, 2))
    status = fields.Char()
    lot = fields.Char()
    remark = fields.Char()  # status for part 1, lot for part 2
    incoming_date = fields.Datetime()
    outgoing_date = fields.Datetime()
    move_date = fields.Datetime()  # for report presentation
    stock_days = fields.Integer()


class StockOfferReportCompute(models.TransientModel):
    """ Here, we just define methods.
    For class fields, go more top at this file.
    """

    _inherit = 'offer.report'

    @api.multi
    # def print_report(self, xlsx_report=False):
    def print_report(self):
        self.ensure_one()
        self.compute_data_for_report()
        report_name = 'stock_offer_report.offer_report'
        return self.env['report'].get_action(records=self,
                                             report_name=report_name)

    def _prepare_report_xlsx(self):
        self.ensure_one()
        return {
            'new_stock_days': self.new_stock_days,
            'stock_threshold_date': self.stock_threshold_date,
            'sales_threshold_date': self.sales_threshold_date,
        }

    @api.multi
    def compute_data_for_report(self):
        self.ensure_one()
        model = self.env['offer.report.line']
        self._create_section_records()
        sections = self.env['offer.report.section'].search(
            [('report_id', '=', self.id)])
        for section in sections:
            self._inject_quant_values(section)
            self._update_qty(model, section)
            self._update_owner(model, section)
            self._update_age(model, section)
            self._update_remark(model, section)
        self.refresh()

    def _create_section_records(self):
        model = self.env['offer.report.section']
        for i in [1, 2]:
            vals = {
                'report_id': self.id,
                'code': i
            }
            model.create(vals)

    def _inject_quant_values(self, section):
        query_inject_quant = ""
        if section.code == 2:
            query_inject_quant += """
WITH
    out_move AS (
        SELECT DISTINCT ON (m.quant_lot_id)
            m.quant_lot_id, m.date
        FROM
            stock_move m
        INNER JOIN
            stock_location loc ON m.location_dest_id = loc.id
        WHERE
            m.picking_type_code = 'outgoing'
            AND loc.usage = 'customer'
            AND active = true
            AND state = 'done'
        ORDER BY
            m.quant_lot_id, m.date DESC
    )
            """
        query_inject_quant += """
INSERT INTO
    offer_report_line
    (
    report_id,
    section_id,
    create_uid,
    create_date,
    category_name,
    quant_id,
    owner_id,
    reservation_id,
    sale_id,
    product_id,
    product_code,
    product_name,
    image_small,
    list_price,
    lot_id,
    lot,
    unit_cost,
    incoming_date
    )
        """
        if section.code == 1:
            query_inject_quant += """
SELECT DISTINCT ON (p.name_template)
            """
        if section.code == 2:
            query_inject_quant += """
SELECT
            """
        query_inject_quant += """
    %s AS report_id,
    %s AS section_id,
    %s AS create_uid,
    NOW() AS create_date,
    pc.name,
    q.id,
    q.original_owner_id,
    q.reservation_id,
    q.sale_id,
    p.id,
    p.default_code,
    p.name_template,
    pt.image_small,
    pt.list_price,
    l.id,
    l.name,
    q.cost,
    q.in_date
FROM
    stock_quant q
INNER JOIN
    product_product p ON q.product_id = p.id
INNER JOIN
    product_template pt ON p.product_tmpl_id = pt.id
INNER JOIN
    product_category pc ON pt.categ_id = pc.id
INNER JOIN
    stock_production_lot l ON q.lot_id = l.id
INNER JOIN
    stock_location loc ON q.location_id = loc.id
            """
        if section.code == 1:
            query_inject_quant += """
WHERE
    loc.usage = 'internal'
    AND q.reservation_id is null
    AND q.sale_id is null
    AND q.in_date >= %s
            """
        if section.code == 2:
            query_inject_quant += """
LEFT OUTER JOIN
    out_move ON l.id = out_move.quant_lot_id
WHERE
    (
    loc.usage = 'internal'
    AND (
        reservation_id is not null
        OR sale_id is not null
        )
    )
    OR loc.usage = 'customer'
    AND (
        out_move.date >= %s
        OR out_move.date is null
        )
            """
        if section.code == 1:
            query_inject_quant += """
ORDER BY
    p.name_template, cost ASC
            """
        if section.code == 1:
            threshold_date = section.report_id.stock_threshold_date
        elif section.code == 2:
            threshold_date = section.report_id.sales_threshold_date
        query_inject_quant_params = (
            self.id,
            section.id,
            self.env.uid,
            threshold_date,
        )

        self.env.cr.execute(query_inject_quant, query_inject_quant_params)

    def _update_qty(self, model, section):
        quant_obj = self.env['stock.quant']
        locs = self.env['stock.location'].search([
            ('usage', '=', 'internal'),
            ('active', '=', True),
        ])
        lines = model.search([('section_id', '=', section.id)])
        for line in lines:
            qty = 1
            if section.code == 1:
                qty = quant_obj.search_count([
                    ('product_id', '=', line.product_id.id),
                    ('location_id', 'in', [loc.id for loc in locs]),
                ])
            if line.list_price:
                margin_percent = 1 - (line.unit_cost / line.list_price)
            else:
                margin_percent = 0
            line.write({'qty': qty, 'margin_percent': margin_percent})

    def _update_owner(self, model, section):
        lines = model.search([('section_id', '=', section.id)])
        for line in lines:
            if line.owner_id.ref:
                owner_name = line.owner_id.ref
            else:
                owner_name = line.owner_id.name
            line.write({'owner_name': owner_name})

    def _update_age(self, model, section):
        lines = model.search([('section_id', '=', section.id)])
        for line in lines:
            out_date = fields.Datetime.to_string(datetime.today())
            if section.code == 1:
                move_date = line.incoming_date
            elif section.code == 2:
                locs = self.env['stock.location'].search([
                    ('usage', '=', 'customer'),
                    ('active', '=', True),
                ])
                move = self.env['stock.move'].search([
                    ('quant_lot_id', '=', line.lot_id.id),
                    ('picking_type_code', '=', 'outgoing'),
                    ('location_dest_id', 'in', [loc.id for loc in locs]),
                    ('state', '=', 'done'),
                ], order='date desc', limit=1)
                if move:
                    out_date = move.date
                move_date = out_date
            stock_days = (
                fields.Datetime.from_string(out_date) - \
                fields.Datetime.from_string(line.incoming_date)
            ).days
            line.write({
                'outgoing_date': out_date,
                'move_date': move_date,
                'stock_days': stock_days,
            })

    def _update_remark(self, model, section):
        lines = model.search([('section_id', '=', section.id)])
        for line in lines:
            if section.code == 1:
                if line.stock_days <= self.new_stock_days:
                    status = 'New Stock!'
                else:
                    status = 'In Stock'
                line.write({'remark': status})
            elif section.code == 2:
                remark = line.lot
                if line.reservation_id:
                    remark += "\nSold!: " + \
                              line.reservation_id.name_get()[0][1]
                elif line.sale_id:
                    remark += "\nReserved: " + line.sale_id.name
                else:
                    remark += "\nSold & Delivered!"
                line.write({'remark': remark})


class StockOfferXslx(stock_abstract_report_xlsx.StockAbstractReportXslx):

    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(StockOfferXslx, self).__init__(
            name, table, rml, parser, header, store)

    def _get_report_name(self):
        return _('Stock Offer Report')

    def _get_report_columns(self, report):
        return {
            0: {'header': _('Brand'), 'field': 'category_name', 'width': 20},
            1: {'header': _('Image'), 'field': 'image_small',
                'type': 'image', 'width': 10},
            2: {'header': _('Code'), 'field': 'product_code', 'width': 10},
            3: {'header': _('Reference Name'), 'field': 'product_name',
                'width': 30},
            4: {'header': _('Qty'), 'field': 'qty', 'type': 'number',
                'width': 5},
            5: {'header': _('HK Retail'), 'field': 'list_price',
                'type': 'amount', 'width': 12},
            6: {'header': _('Unit Cost'), 'field': 'unit_cost',
                'type': 'amount', 'width': 12},
            7: {'header': _('Margin %'), 'field': 'margin_percent',
                'type': 'percent', 'width': 8},
            8: {'header': _('Owner/Contact Ref.'), 'field': 'owner_name',
                'width': 18},
            9: {'header': _('Incoming Date'), 'field': 'move_date',
                'width': 20},
            10: {'header': _('Days in Stock'), 'field': 'stock_days',
                'type': 'number', 'width': 10},
            11: {'header': _('Status'), 'field': 'remark', 'width': 20},
        }

    def _get_report_filters(self, report):
        return [
            [_('Report Date'), report.current_date],
            [_('New Stock Days'), report.new_stock_days],
            [_('Stock Threshold Date'), report.stock_threshold_date],
            [_('Sales Threshold Date'), report.sales_threshold_date],
        ]

    def _get_col_count_filter_name(self):
        return 2

    def _get_col_count_filter_value(self):
        return 2

    def _generate_report_content(self, workbook, report):
        title_vals = {
            1: 'Part 1. In Stock',
            2: 'Part 2. Sold/Reserved',
        }
        for section in report.section_ids:
            self.write_array_title(title_vals[section.code])

            if section.code == 1:
                self.write_array_header()
            # adjust array header
            elif section.code == 2:
                adj_col = {
                    9: _('Outgoing/Current Date'),
                    11: _('Case No. & Status')
                }
                self.write_array_header(adj_col)

            # sort output by product_name and lot
            sorted_quants = sorted(
                section.quant_ids,
                key=lambda x: (x.product_name, x.lot)
            )
            for quant in sorted_quants:
                self.write_line(quant, height=50)

            # Line break
            self.row_pos += 2

        params = [
            {'col': 11, 'vals': ['New Stock!', 'Sold']},
        ]
        self._apply_conditional_format(params)


StockOfferXslx(
    'report.stock_offer_report.offer_report',
    'offer.report',
    parser=report_sxw.rml_parse
)
