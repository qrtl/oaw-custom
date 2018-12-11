# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.exceptions import Warning
from openerp.addons.web.controllers.main import Action
from openerp import http
from openerp.http import request
from openerp.tools.translate import _


class Action(Action):

    @http.route('/web/action/load', type='json', auth="user")
    def load(self, action_id, do_not_eval=False, additional_context=None):
        action_access = False
        if action_id:
            action = request.env['ir.actions.act_window'].search([
                ('id', '=', int(action_id))
            ])
            if action and action.groups_id:
                for group in action.groups_id.ids:
                    if group in request.env.user.groups_id.ids:
                        action_access = True
                        break
            else:
                action_access = True
        if not action_access:
            raise Warning(_('Access Denied'),
                          _("Sorry, you are not allowed to access this "
                            "document."))
        else:
            return super(Action, self).load(action_id, do_not_eval=do_not_eval,
                                            additional_context=additional_context)
