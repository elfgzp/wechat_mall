# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request

from .error_code import error_code
from .. import defs


class OrderCreate(http.Controller):
    @http.route('/<string:test>/', auth='public', methods=['GET'])
    def get(self, test):
        return test
