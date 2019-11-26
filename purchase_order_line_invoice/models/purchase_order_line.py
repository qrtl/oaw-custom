# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    invoiced = fields.Boolean(
        string="Invoiced", compute="_compute_invoiced", store=True
    )
    partner_ref = fields.Char(
        related="order_id.partner_ref", string="Vendor Reference", store=True
    )
    image_medium = fields.Binary(related="product_id.image_medium", string="image")

    @api.multi
    @api.depends("qty_invoiced", "product_qty")
    def _compute_invoiced(self):
        for line in self:
            line.invoiced = False if line.qty_invoiced < line.product_qty else True

    @api.multi
    def makeInvoices(self):
        context = self.env.context or {}
        record_ids = context.get("active_ids", [])

        if record_ids:
            res = False
            invoices = {}
            purchase_obj = self.env["purchase.order"]
            purchase_line_obj = self.env["purchase.order.line"]
            invoice_line_obj = self.env["account.invoice.line"]

            for line in purchase_line_obj.browse(record_ids):
                if not line.invoiced and (line.state not in ("draft", "cancel")):
                    if line.partner_id.id not in invoices:
                        invoices[line.partner_id.id] = []
                    invoice_line_vals = line._prepare_invoice_line_vals()
                    invoice_line_vals.update({"origin": line.order_id.name})
                    invoice_line = invoice_line_obj.create(invoice_line_vals)
                    line.write(
                        {
                            "qty_invoiced": line.qty_invoiced
                            or 0 + invoice_line.quantity,
                            "invoice_lines": [(4, invoice_line.id)],
                        }
                    )
                    invoices[line.partner_id.id].append((line, invoice_line))
            res = []
            for result in invoices.values():
                invoice_line_ids = list(map(lambda x: x[1].id, result))
                orders = list(set(map(lambda x: x[0].order_id, result)))
                res.append(
                    self._make_invoice_by_partner(
                        orders[0].partner_id, orders, invoice_line_ids
                    )
                )
        return {
            "name": _("Supplier Invoices"),
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "account.invoice",
            "domain": "[('id','in', [" + ",".join(map(str, res)) + "])]",
            "view_id": False,
            "context": "{'type':'in_invoice', 'journal_type': 'purchase'}",
            "type": "ir.actions.act_window",
        }

    @api.multi
    def _prepare_invoice_line_vals(self):
        self.ensure_one()
        return {
            "name": self.name,
            "account_id": self.order_id.partner_id.property_account_payable_id.id,
            "price_unit": self.price_unit or 0.0,
            "quantity": self.product_qty,
            "product_id": self.product_id.id or False,
            "invoice_line_tax_ids": [(6, 0, [x.id for x in self.taxes_id])],
            "purchase_line_id": self.id,
        }

    def _make_invoice_by_partner(self, partner, orders, lines_ids):
        """
            create a new invoice for one supplier
            @param partner : The object partner
            @param orders : The set of orders to add in the invoice
            @param lines : The list of line's id
        """
        purchase_obj = self.env["purchase.order"]
        account_journal_obj = self.env["account.journal"]
        invoice_obj = self.env["account.invoice"]
        name = orders and ",".join([order.name for order in orders]) or ""
        journal_id = account_journal_obj.search([("type", "=", "purchase")])
        journal_id = journal_id and journal_id[0].id or False
        account_id = partner.property_account_payable_id.id
        invoice_vals = {
            "name": name,
            "origin": name,
            "type": "in_invoice",
            "journal_id": journal_id,
            "reference": partner.ref,
            "account_id": account_id,
            "partner_id": partner.id,
            "invoice_line_ids": [(6, 0, lines_ids)],
            "currency_id": orders[0].currency_id.id,
            "comment": " \n".join([order.notes for order in orders if order.notes]),
            "payment_term_id": orders[0].payment_term_id.id,
            "fiscal_position_id": partner.property_account_position_id.id,
        }
        invoice_id = invoice_obj.create(invoice_vals).id
        for order in orders:
            order.write({"invoice_ids": [(4, invoice_id)]})
        return invoice_id
