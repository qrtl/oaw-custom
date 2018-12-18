# -*- coding: utf-8 -*-
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import xmlrpclib
import logging
import werkzeug.serving
import werkzeug.contrib.fixers
import openerp

_logger = logging.getLogger(__name__)

BROWSER_LIST = ['Mozilla', 'AppleWebKit', 'Chromium', 'Chrome', 'Safari']


def wsgi_xmlrpc(environ, start_response):
    """ Two routes are available for XML-RPC

    /xmlrpc/<service> route returns faultCode as strings. This is a historic
    violation of the protocol kept for compatibility.

    /xmlrpc/2/<service> is a new route that returns faultCode as int and is
    therefore fully compliant.
    """
    # API restriction
    #----------------------------------------------------------
    if environ:
        restrcit_call = True
        HTTP_USER_AGENT = environ.get('HTTP_USER_AGENT')
        for browser in BROWSER_LIST:
            if browser in HTTP_USER_AGENT:
                restrcit_call = False

        if restrcit_call:
            response = 'No handler found.\n'
            start_response('404 Not Found', [('Content-Type', 'text/plain'), ('Content-Length', str(len(response)))])
            return [response]

    #----------------------------------------------------------
    if environ['REQUEST_METHOD'] == 'POST' and environ['PATH_INFO'].startswith('/xmlrpc/'):
        length = int(environ['CONTENT_LENGTH'])
        data = environ['wsgi.input'].read(length)

        # Distinguish betweed the 2 faultCode modes
        string_faultcode = True
        if environ['PATH_INFO'].startswith('/xmlrpc/2/'):
            service = environ['PATH_INFO'][len('/xmlrpc/2/'):]
            string_faultcode = False
        else:
            service = environ['PATH_INFO'][len('/xmlrpc/'):]

        params, method = xmlrpclib.loads(data)
        return xmlrpc_return(start_response, service, method, params, string_faultcode)

openerp.service.wsgi_server.wsgi_xmlrpc = wsgi_xmlrpc
