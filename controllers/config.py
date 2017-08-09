# -*- coding: utf-8 -*-

import json

from odoo import http

from .error_code import error_code


class ConfigGetValue(http.Controller):
    @http.route('/<model("res.users"):user>/config/get_value', auth='public')
    def get(self, user, key=None):
        if not key:
            return json.dumps({'code': 300, 'msg': error_code[300]})

        config = http.request.env['wechat_mall.config.settings']
        value_obj = config.get_config(key, uid=user.id, obj=True)
        if not value_obj:
            return json.dumps({'code': 404, 'msg': error_code[404]})

        response = {
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
        }
        return json.dumps(response)
