# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    order_ref_fm_report = fields.Char(string="Order Reference", readonly=True)
    supplier_id = fields.Many2one(
        "res.partner", string="Sales Supplier"
    )

    @api.multi
    def print_supplier_quotation(self):
        self.filtered(lambda s: s.state == "draft").write({"state": "sent"})
        return self.env.ref(
            "supplier_user_access.report_sale_supplier_fm"
        ).report_action(self)

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        # For quotation adjust: set new order_ref field
        if "name" in vals and "partner_id" in vals:
            name = vals["name"]
            # Get the reference number number
            fragments_order_ref = vals["name"].split("-")
            sub_order_ref = fragments_order_ref[-1]
            res.order_ref_fm_report = sub_order_ref
        return res

    def action_supplier_view_delivery(self):
        result = self.env.ref("supplier_user_access.action_picking_tree_all")

        # compute the number of delivery orders to display
        picking_ids = []
        for order in self:
            picking_ids += [picking.id for picking in order.picking_ids]

        # choose the view_mode accordingly
        if len(picking_ids) > 1:
            result.domain = "[('id','in',[" + \
                ",".join(map(str, picking_ids)) + "])]"
        else:
            form_view = self.env.ref(
                "supplier_user_access.view_supplier_picking_form")
            result.views = [(form_view and form_view[1] or False, "form")]
            result.res_id = picking_ids and picking_ids[0] or False

        return result
