# -*- coding: utf-8 -*-
# Copyright 2016 Rooms For (Hong Kong) Limited T/A OSCG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields


from . import abstract_report_xlsx
from openerp.report import report_sxw
from openerp import _


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
    category = fields.Char()


class ConsignmentReportQuant(models.TransientModel):

    _name = 'consignment_report_quant'
    # _order = 'name ASC'

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

    # Data fields, used for report display
    product_code = fields.Char()
    product_name = fields.Char()
    lot_name = fields.Char()


class ConsignmentReportCompute(models.TransientModel):
    """ Here, we just define methods.
    For class fields, go more top at this file.
    """

    _inherit = 'consignment_report'

    @api.multi
    def print_report(self, xlsx_report=False):
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
        self._create_section_records()
        sections = self.env['consignment_report_section'].search(
            [('report_id', '=', self.id)])
        for section in sections:
            self._inject_quant_values(section.id)
        self.refresh()

    def _create_section_records(self):
        model = self.env['consignment_report_section']
        vals = {
            'report_id': self.id,
            'category': 'Part 1'
        }
        model.create(vals)

    def _inject_quant_values(self, section_id):
        query_inject_quant = """
INSERT INTO
    consignment_report_quant
    (
    report_id,
    section_id,
    create_uid,
    create_date,
    quant_id,
    product_code,
    product_name,
    lot_name
    )
SELECT
    %s AS report_id,
    %s AS section_id,
    %s AS create_uid,
    NOW() AS create_date,
    q.id,
    p.default_code,
    p.name_template,
    l.name
FROM
    stock_quant q
INNER JOIN
    product_product p
        on q.product_id = p.id
INNER JOIN
    stock_production_lot l
        on q.lot_id = l.id
        """
        query_inject_quant_params = (
            self.id,
            section_id,
            self.env.uid,
        )
        self.env.cr.execute(query_inject_quant, query_inject_quant_params)


class PartnerXslx(abstract_report_xlsx.AbstractReportXslx):

    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(PartnerXslx, self).__init__(
            name, table, rml, parser, header, store)

    def _get_report_name(self):
        return _('Consignment Report')

    def _get_report_columns(self, report):
        return {
            0: {'header': _('Code'), 'field': 'product_code', 'width': 15},
            1: {'header': _('Reference Name'), 'field': 'product_name',
                'width': 30},
            2: {'header': _('Case No.'), 'field': 'lot_name', 'width': 15},
        }

    def _get_report_filters(self, report):
        return [
        ]

    def _get_col_count_filter_name(self):
        return 2

    def _get_col_count_filter_value(self):
        return 3

    def _generate_report_content(self, workbook, report):

        for section in report.section_ids:
            self.write_array_title(section.category)

            self.write_array_header()

            # self.write_line()
            # model = self.env['report_partner_xlsx_partner']
            # for p in model.search([('partner_id','=',partner.id)]):
            #     self.write_line(p)
            for quant in section.quant_ids:
                self.write_line(quant)

            # Line break
            self.row_pos += 2


PartnerXslx(
    'report.stock_consignment_report.consignment_report',
    'consignment_report',
    parser=report_sxw.rml_parse
)
