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

    # Filters fields, used for data computation
    filter_partner_id = fields.Many2one(comodel_name='res.partner')
    threshold_date= fields.Date()
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
    category_name = fields.Char()
    product_code = fields.Char()
    product_name = fields.Char()
    qty = fields.Integer()
    image_small = fields.Binary()
    list_price = fields.Float()
    margin_percent = fields.Float()
    lot = fields.Char()
    # currency = fields.Char()
    # purchase_price = fields.Float(digits=(16, 2))
    unit_cost = fields.Float(digits=(16, 2))
    status = fields.Char()
    remark = fields.Char()
    incoming_date = fields.Datetime()
    stock_days = fields.Integer()
    quant_last_updated = fields.Datetime()


class StockOfferReportCompute(models.TransientModel):
    """ Here, we just define methods.
    For class fields, go more top at this file.
    """

    _inherit = 'offer.report'

    @api.multi
    def print_report(self, xlsx_report=False):
        self.ensure_one()
        self.compute_data_for_report()
        report_name = 'stock_offer_report.offer_report'
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
        model = self.env['offer.report.line']
        self._create_section_records()
        sections = self.env['offer.report.section'].search(
            [('report_id', '=', self.id)])
        for section in sections:
            self._inject_quant_values(section)
            self._update_qty(model, section)
            if section.code == 1:
                self._update_reservation(model, section.id)
            elif section.code == 2:
                self._update_invoice_info(section.id, section.code)
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
        query_inject_quant = """
INSERT INTO
    offer_report_line
    (
    report_id,
    section_id,
    create_uid,
    create_date,
    category_name,
    quant_id,
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
    status,
    incoming_date,
    quant_last_updated
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
    %s AS status,
    q.in_date,
    q.write_date
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
        query_inject_quant += """
WHERE loc.usage = %s
    AND q.original_owner_id = %s
        """
        if section.code == 2:
            query_inject_quant += """
    AND q.write_date >= %s
            """
        status_desc = {
            2: 'Sold',
            1: 'In Stock',
        }
        loc_usage = {
            2: 'customer',
            1: 'internal',
        }
        if section.code == 1:
            query_inject_quant += """
ORDER BY
    p.name_template, cost ASC
            """
        if section.code == 2:
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
    offer_report_line line1
SET
    currency = inv_info.curr,
    purchase_price = inv_info.price,
    remark = inv_info.supp_invoice
FROM (
    SELECT
        inv.currency AS curr,
        inv.price_unit AS price,
        inv.supp_invoice,
        line2.section_id,
        inv.lot_id
    FROM
        offer_report_line line2
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
        ON line2.lot_id = inv.lot_id
    WHERE
        line2.section_id = %s
) inv_info
WHERE
    line1.section_id = inv_info.section_id
    AND line1.lot_id = inv_info.lot_id
        """
        state_vals = {
            2: ('paid', 'draft', 'open'),
        }
        query_update_quant_params = (
            state_vals[code],
            section_id,
        )
        self.env.cr.execute(query_update_quant, query_update_quant_params)

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

    def _update_reservation(self, model, section_id):
        quants = model.search([('section_id', '=', section_id)])
        for quant in quants:
            stock_days = (
                datetime.today() - \
                fields.Datetime.from_string(quant.incoming_date)
            ).days
            quant.write({'stock_days': stock_days})
            if quant.reservation_id:
                quant.write({
                    'remark': quant.reservation_id.name_get()[0][1]})
            elif quant.sale_id:
                quant.write({'remark': quant.sale_id.name})


class StockOfferXslx(stock_abstract_report_xlsx.AbstractReportXslx):

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
            # 4: {'header': _('Case No.'), 'field': 'lot', 'width': 15},

            5: {'header': _('HK Retail'), 'field': 'list_price',
                'type': 'amount', 'width': 12},
            6: {'header': _('Unit Cost'), 'field': 'unit_cost',
                'type': 'amount', 'width': 12},
            7: {'header': _('Margin %'), 'field': 'margin_percent',
                'type': 'percent', 'width': 8},
            8: {'header': _('Status'), 'field': 'status', 'width': 18},
            9: {'header': _('Remark'), 'field': 'remark', 'width': 30},
            10: {'header': _('Incoming Date'), 'field': 'incoming_date',
                'width': 20},
            11: {'header': _('Age'), 'field': 'stock_days',
                'type': 'number', 'width': 8},
            12: {'header': _('Last Updated'), 'field': 'quant_last_updated',
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
            1: 'Part 1. In Stock',
            2: 'Part 2. Sold',
        }
        for section in report.section_ids:
            self.write_array_title(title_vals[section.code])

            self.write_array_header()

            for quant in section.quant_ids:
                self.write_line(quant, 50)  # 50 being row height

            # Line break
            self.row_pos += 2


StockOfferXslx(
    'report.stock_offer_report.offer_report',
    'offer.report',
    parser=report_sxw.rml_parse
)
