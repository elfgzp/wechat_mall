# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request

from .. import defs
from .error_code import error_code


class BannerList(http.Controller):
    @http.route('/<string:sub_domain>/banner/list', auth='public', methods=['GET'])
    def get(self, sub_domain):
        try:
            user = request.env['res.users'].sudo().search([('sub_domain', '=', sub_domain)])
            if not user:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            banner_list = request.env['wechat_mall.banner'].search([
                ('create_uid', '=', user.id),
                ('status', '=', True)
            ])
            if not banner_list:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            response = request.make_response(
                headers={
                    "Content-Type": "json"
                },
                data=json.dumps({
                    "code": 0,
                    "data": [
                        {
                            "businessId": each_banner.business_id.id,
                            "dateAdd": each_banner.create_date,
                            "dateUpdate": each_banner.write_date,
                            "id": each_banner.id,
                            "linkUrl": each_banner.link_url or '',
                            "paixu": each_banner.sort or 0,
                            "picUrl": each_banner.pic.static_link(),
                            "remark": each_banner.remark or '',
                            "status": 0 if each_banner.status else 1,
                            "statusStr": defs.BannerStatus.attrs[each_banner.status],
                            "title": each_banner.title,
                            "type": each_banner.type_mark,
                            "userId": each_banner.create_uid.id
                        } for each_banner in banner_list
                    ],
                    "msg": "success"
                })
            )

            return response

        except Exception as e:
            return request.make_response(json.dumps({'code': -1, 'msg': error_code[-1], 'data': e.message}))
