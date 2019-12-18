# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, http
from odoo.addons.web.controllers.main import Action
from odoo.exceptions import Warning
from odoo.http import request


class Action(Action):
    @http.route("/web/action/load", type="json", auth="user")
    def load(self, action_id, additional_context=None):
        action_access = False
        if action_id:
            action = request.env["ir.actions.act_window"].search(
                [("id", "=", int(action_id))]
            )
            if action and action.groups_id:
                for group in action.groups_id.ids:
                    if group in request.env.user.groups_id.ids:
                        action_access = True
                        break
            else:
                action_access = True
        if not action_access:
            raise Warning(_("Sorry, you are not allowed to access this " "document."))
        else:
            return super(Action, self).load(
                action_id, additional_context=additional_context
            )
