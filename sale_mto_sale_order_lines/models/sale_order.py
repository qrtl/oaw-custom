# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo import SUPERUSER_ID


class SaleOrder(models.Model):
    _inherit = "sale.order"

    supplier_id = fields.Many2one(
        comodel_name='res.partner',
        string="Sales Supplier",
        store=True
        # default = lambda self: self.env.user.partner_id
    )
    supplier_code = fields.Char(
        'Code',
        related='supplier_id.ref',
        store=True

    )
    is_shipment = fields.Boolean(
        'Shipment',
    )

    def create(self, vals):
        if vals['is_mto']:
            user = self.env.user
            print("cheers")
            if user.has_group('supplier_user_access.group_supplier'):
                print("cheers")
        res = super(SaleOrder, self).create(vals)
        return res
        #         # Supplier creates MTO: it must be is_shipment (this field will also be invisible for supplier)
        #         if user.has_group('model_security_adjust_oaw.group_supplier'):
        #             vals['is_shipment'] = True
        #             print "Suppliers mto and shipment"
        #         # Internal MTO: supplier_id must be selected
        #         if not user.has_group('model_security_adjust_oaw.group_supplier'):
        #             if 'supplier_id' in vals:
        #                 if not vals['supplier_id']:
        #                     raise osv.except_osv(_('Error!'), _('For MTO, you must select "Sales Supplier"'))
        #
        #
        # res = super(SaleOrderOsv, self).create(cr, uid, vals, context=context)
        # rec = self.browse(cr, uid, res, context=context)
        # if rec.supplier_id:
        #     self.message_subscribe(cr, SUPERUSER_ID, [rec.id], [rec.supplier_id.id], context=context)
        # return res
