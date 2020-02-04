# Copyright 2020 Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Sales Supplier",
        store=True
        # default = lambda self: self.env.user.partner_id
    )
    supplier_code = fields.Char("Code", related="supplier_id.ref", store=True)
    is_shipment = fields.Boolean("Shipment")

    @api.model
    def create(self, vals):
        if vals["is_mto"]:
            user = self.env.user
            # If Supplier creates a MTO, it will be declared as is_shipment
            if user.has_group("supplier_user_access.group_supplier"):
                vals["is_shipment"] = True
            # If internal user creates MTO, user will required to set a Sales Supplier
            if not user.has_group("supplier_user_access.group_supplier"):
                if "supplier_id" in vals:
                    if not vals["supplier_id"]:
                        raise UserError("For MTO a Sales Supplier has to be selected!")
        res = super(SaleOrder, self).create(vals)


        # rec = self.browse(cr, uid, res, context=context)
        # if rec.supplier_id:
        #     self.message_subscribe(cr, SUPERUSER_ID, [rec.id], [rec.supplier_id.id], context=context)
        return res

    @api.multi
    def write(self, vals):
        for rec in self:
            if rec.is_mto:
                user = self.env.user
                # If Supplier creates a MTO, it will be declared as is_shipment
                if user.has_group("supplier_user_access.group_supplier"):
                    vals["is_shipment"] = True
                # If internal user creates MTO, user will required to set a Sales Supplier
                if not user.has_group("supplier_user_access.group_supplier"):
                    if "supplier_id" in vals:
                        if not vals["supplier_id"]:
                            raise UserError("For MTO a Sales Supplier has to be selected!")
        res = super(SaleOrder, self).write(vals)

        # rec = self.browse(cr, uid, res, context=context)
        # if rec.supplier_id:
        #     self.message_subscribe(cr, SUPERUSER_ID, [rec.id], [rec.supplier_id.id], context=context)
        return res
