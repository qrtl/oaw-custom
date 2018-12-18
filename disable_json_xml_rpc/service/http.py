# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import openerp
from openerp.http import CommonController, route, dispatch_rpc


# ----------------------------------------------------------
# RPC controller
# ----------------------------------------------------------
class CommonController(CommonController):

    @route('/jsonrpc', type='json', auth="none")
    def jsonrpc(self, service, method, args):
        """ Method used by client APIs to contact OpenERP. """
        # API restriction
        # ----------------------------------------------------------
        response = 'No handler found.\n'
        start_response('404 Not Found', [('Content-Type', 'text/plain'), (
        'Content-Length', str(len(response)))])
        return [response]
        # ----------------------------------------------------------
        return dispatch_rpc(service, method, args)
