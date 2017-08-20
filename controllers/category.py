# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request

from .. import defs
from .error_code import error_code


import logging

_logger = logging.getLogger(__name__)


class AllCategory(http.Controller):
    @http.route('/<string:sub_domain>/shop/goods/category/all', auth='public', methods=['GET'])
    def get(self, sub_domain):
        user = request.env['res.users'].sudo().search([('sub_domain', '=', sub_domain)])
        if not user:
            return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

        try:
            all_category = request.env['wechat_mall.category'].search([
                ('create_uid', '=', user.id),
                ('is_use', '=', True)
            ])
            if not all_category:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            response = request.make_response(
                headers={
                    "Content-Type": "json"
                },
                data=json.dumps(
                    {
                        "code": 0,
                        "data": [
                            {
                                "dateAdd": each_category.create_date,
                                "dateUpdate": each_category.write_date,
                                "icon": each_category.icon.static_link() if each_category.icon else '',
                                "id": each_category.id,
                                "isUse": each_category.is_use,
                                "key": each_category.key,
                                "level": each_category.level,
                                "name": each_category.name,
                                "paixu": each_category.sort or 0,
                                "pid": each_category.pid.id if each_category.pid else 0,
                                "type": each_category.category_type,
                                "userId": each_category.create_uid.id
                            } for each_category in all_category
                        ],
                        "msg": "success"
                    })
            )

            return response
        except Exception as e:
            _logger.exception(e)
            return request.make_response(json.dumps({'code': -1, 'msg': error_code[-1], 'data': e.message}))
