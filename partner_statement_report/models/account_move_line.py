# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    reconcile_invoice = fields.Char(
        'Reconciled Invoice',
        compute="_get_reconcile_info",
        readonly=True,
        store=True
    )
    reconcile_order = fields.Char(
        'Reconciled Sales Order',
        compute="_get_reconcile_info",
        readonly=True,
        store=True
    )
    reconcile_item = fields.Char(
        'Reconciled Journal Items',
        compute="_get_reconcile_info",
        readonly=True,
        store=True
    )

    @api.multi
    @api.depends('reconcile_id', 'reconcile_partial_id')
    def _get_reconcile_info(self):
        for aml in self:
            if not aml.invoice and aml.journal_id.type <> "situation":
                aml.reconcile_invoice = ''
                domain = False
                if aml.reconcile_partial_id:
                    domain = [(
                        ('reconcile_partial_id', '=',
                         aml.reconcile_partial_id.id)
                    )]
                if aml.reconcile_id:
                    domain = [(
                        ('reconcile_id', '=', aml.reconcile_id.id)
                    )]
                if domain:
                    related_items = self.env['account.move.line'].search(
                        domain)
                    invoice_list = []
                    order_list = []
                    reconcile_item = []
                    for item in related_items:
                        if item.invoice:
                            if item.invoice.number not in invoice_list:
                                invoice_list.append(item.invoice.number)
                            for invoice_line in item.invoice.invoice_line:
                                if invoice_line.so_id and \
                                   invoice_line.so_id.name not in order_list:
                                    order_list.append(invoice_line.so_id.name)
                        else:
                            if item.move_id.name not in reconcile_item and \
                                    item.id <> aml.id:
                                reconcile_item.append(item.move_id.name)
                    aml.reconcile_invoice = ','.join(invoice_list) if len(
                        invoice_list) > 0 else False
                    aml.reconcile_order = ','.join(order_list) if len(
                        order_list) > 0 else False
                    aml.reconcile_item = ','.join(reconcile_item) if len(
                        reconcile_item) > 0 else False
