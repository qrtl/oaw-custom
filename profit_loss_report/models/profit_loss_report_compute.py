# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields, _
from openerp.addons.abstract_report_xlsx.reports \
    import stock_abstract_report_xlsx
from openerp.report import report_sxw


class ProfitLossReportCompute(models.TransientModel):
    _inherit = 'profit.loss.report'

    def _inject_data(self, section):
        query = """
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
            product_id,
            product_code,
            product_name,
            image_small,
            list_price,
            unit_cost,
            net_price,
            placeholder1
            )
        SELECT DISTINCT ON (p.name_template)
            %s AS report_id,
            %s AS section_id,
            %s AS create_uid,
            NOW() AS create_date,
            pc.name,
            q.id,
            q.original_owner_id,
            p.id,
            p.default_code,
            p.name_template,
            pt.image_small,
            pt.list_price,
            q.cost,
            pt.net_price,
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
            stock_location loc ON q.location_id = loc.id
        WHERE
            loc.usage = 'internal'
            AND q.reservation_id is null
            AND q.sale_id is null
            AND q.in_date >= %s
        """
        query_params = (
            self.id,
            section.id,
            self.env.uid,
            section.report_id.stock_threshold_date or '1900-01-01',
            )
        self.env.cr.execute(query, query_params)
