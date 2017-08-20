# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request

from .error_code import error_code


import logging

_logger = logging.getLogger(__name__)



class ConfigGetValue(http.Controller):
    @http.route('/<string:sub_domain>/config/get_value', auth='public', methods=['GET'])
    def get(self, sub_domain, key=None):
        try:
            user = request.env['res.users'].sudo().search([('sub_domain', '=', sub_domain)])
            if not user:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            if not key:
                return request.make_response(json.dumps({'code': 300, 'msg': error_code[300].format('key')}))

            config = request.env['wechat_mall.config.settings']
            value_obj = config.get_config(key, uid=user.id, obj=True)
            if not value_obj:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            response = request.make_response(
                headers={
                    "Content-Type": "json"
                },
                data=json.dumps({
                    'code': 0,
                    'data': {
                        'creatAt': value_obj.create_date,
                        'dateType': 0,
                        'id': value_obj.id,
                        'key': key,
                        'remark': '',
                        'updateAt': value_obj.write_date,
                        'userId': user.id,
                        'value': config.get_config(key, uid=user.id)
                    },
                    'msg': 'success'
                })
            )
            return response
        except AttributeError:
            return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

        except Exception as e:
            _logger.exception(e)
            return request.make_response(json.dumps({'code': -1, 'msg': error_code[-1], 'data': e.message}))
