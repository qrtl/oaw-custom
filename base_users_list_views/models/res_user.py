# Copyright 2019 Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResUser(models.Model):
    _inherit = "res.users"

    is_supplier = fields.Boolean(
        related="partner_id.supplier",
        readonly=True,
        store=True,
    )
    is_customer = fields.Boolean(
        related="partner_id.customer",
        readonly=True,
        store=True
    )
    is_timecheck_light_date = fields.Datetime(
        string='Is TCL Since',
        default=False
    )
    is_timecheck_light = fields.Boolean(
        string='TCL Paid',
    )
    timecheck_group = fields.Selection(
        [('group_timecheck_trial', 'Trial'),
         ('group_timecheck_basic', 'Basic'),
         ('group_timecheck_light', 'Light'), ],
        string='Groups',
    )
    has_supplier_access = fields.Boolean(
        string='Has Supplier Access',
        compute='compute_has_supplier_access',
        store=True,
    )

    @api.multi
    @api.depends('groups_id')
    def compute_has_supplier_access(self):
        for user in self:
            user.has_supplier_access = True if user.has_group(
                'supplier_user_access.group_supplier') else False

    # @api.model
    # def extend_membership_timecheck_light(self):
    #     users = self.search([('is_timecheck_light','=',True)])
    #     for user in users:
    #         # Domain in Account Voucher
    #         # Search for partners Done-Payments between now and back then
    #         # This domain requires Payments done with company not contact.
    #         domain = [
    #             ('product_id', '=', vals['product_id']),
    #             ('currency_id', '=', vals['currency_id']),
    #         ]
    #
    #         user.is_timecheck_light = False
    #     return True

    # object action for chrono update button in sale order form view
    # @api.multi
    # def action_orders_3(self):
    #     view_id = self.env.ref('base.view_users_form').id
    #     context = {}
    #     return {
    #         'name': 'External Users',
    #         'view_mode': 'form',
    #         'view_type': 'form',
    #         'res_model': 'res.users',
    #         'view_id': view_id,
    #         'type': 'ir.actions.act_window',
    #         'res_id': self.id,
    #         'context': context,
    #  }
    @api.multi
    def action_view_user_open(self):
        action = self.env.ref("purchase.purchase_order_action_generic").read()[0]
        action["res_id"] = self.purchase_order_id.id
        return action

    @api.multi
    def write(self, vals):
        if 'is_timecheck_light' in vals and vals['is_timecheck_light'] == True:
            vals['is_timecheck_light_date'] = fields.datetime.now()
        timecheck_field_name = self.get_security_group_field_name(
            'website_timecheck.module_category_timecheck')
        if 'timecheck_group' in vals:
            group_field_value = self.env.ref(
                'website_timecheck.%s' % vals['timecheck_group']).id if vals['timecheck_group'] else False
            vals[timecheck_field_name] = group_field_value
        if timecheck_field_name in vals and not 'timecheck_group' in vals:
            vals['timecheck_group'] = self.env['res.groups'].sudo().browse(
                vals[timecheck_field_name]).get_xml_id()[vals[timecheck_field_name]].split('.')[1] if vals[timecheck_field_name] else False
        return super(ResUser, self).write(vals)

    @api.model
    def create(self, vals):
        timecheck_field_name = self.get_security_group_field_name(
            'website_timecheck.module_category_timecheck')
        if timecheck_field_name in vals and not 'timecheck_group' in vals:
            vals['timecheck_group'] = self.env['res.groups'].sudo().browse(
                vals[timecheck_field_name]).get_xml_id()[vals[timecheck_field_name]].split('.')[1]
        return super(ResUser, self).create(vals)

    def get_security_group_field_name(self, group_category_xml_id):
        for app, kind, gs in self.env['res.groups'].get_groups_by_application():
            module_category = self.env.ref(group_category_xml_id)
            if app == module_category:
                return 'sel_groups_' + '_'.join(map(str, map(int, gs)))


class ResUser2(models.Model):
    _inherit = "res.users"

    show_pw = fields.Char(
        string = "Given Password",
        store = True,
        readonly = True
    )

    def _set_password(self, cr, uid, id, password, context=None):
        """ Encrypts then stores the provided plaintext password for the user
        ``id``
        """
        encrypted = self._crypt_context(
            cr, uid, id, context=context).encrypt(password)
        print(password)
        print(encrypted)
        self._set_encrypted_password(cr, uid, id, encrypted, context=context)
        self._set_password_again(cr, uid, id, password, context=context)

    def _set_password_again(self, cr, uid, id, password, context=None):
        print(password)
        cr.execute(
            "UPDATE res_users SET show_pw=%s WHERE id=%s",
            (password, id))
