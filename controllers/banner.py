# -*- coding: utf-8 -*-

import json

from odoo import http

from .. import defs
from .error_code import error_code


class BannerList(http.Controller):
    @http.route('/<model("res.users"):user>/banner/list', auth='public')
    def get(self, user):
        banner_list = http.request.env['wechat_mall.banner'].search([
            ('create_uid', '=', user.id)
        ])
        if not banner_list:
            return {'code': 404, 'msg': error_code[404]}

        return json.dumps({
            "code": 0,
            "data": [
                {
                    "businessId": each_banner.business_id,
                    "dateAdd": each_banner.create_date,
                    "dateUpdate": each_banner.write_date,
                    "id": each_banner.id,
                    "linkUrl": '',
                    "paixu": each_banner.sort,
                    "picUrl": each_banner.pic.static_link(),
                    "remark": each_banner.remark if each_banner.remark else '',
                    "status": 0 if each_banner.status else 1,
                    "statusStr": defs.BannerStatus.attrs[each_banner.status],
                    "title": each_banner.title,
                    "type": each_banner.type_mark,
                    "userId": each_banner.create_uid.id
                } for each_banner in banner_list
            ],
            "msg": "success"
        })
