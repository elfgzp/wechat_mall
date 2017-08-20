# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request

from .. import defs
from .error_code import error_code

import logging

_logger = logging.getLogger(__name__)


class BannerList(http.Controller):
    @http.route('/<string:sub_domain>/banner/list', auth='public', methods=['GET'])
    def get(self, sub_domain, default_banner=True):
        try:
            user = request.env['res.users'].sudo().search([('sub_domain', '=', sub_domain)])
            if not user:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            banner_list = request.env['wechat_mall.banner'].search([
                ('create_uid', '=', user.id),
                ('status', '=', True)
            ])

            data = []
            if banner_list:
                data = [
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
                ]

            recommend_goods = request.env(user=user.id)['wechat_mall.goods'].search([
                ('create_uid', '=', user.id),
                ('recommend_status', '=', True),
                ('status', '=', True)
            ], limit=5)

            data += [
                {
                    "goods": True,
                    "businessId": goods.id,
                    "dateAdd": goods.create_date,
                    "dateUpdate": goods.write_date,
                    "id": goods.id,
                    "linkUrl": '',
                    "paixu": goods.sort or 0,
                    "picUrl": goods.pic[0].static_link() if goods.pic else '',
                    "remark": '',
                    "status": 0 if goods.status else 1,
                    "statusStr": '',
                    "title": goods.name,
                    "type": 0,
                    "userId": goods.create_uid.id
                } for goods in recommend_goods
            ]

            response = request.make_response(
                headers={
                    "Content-Type": "json"
                },
                data=json.dumps({
                    "code": 0,
                    "data": data,
                    "msg": "success"
                })
            )

            return response

        except Exception as e:
            _logger.exception(e)
            return request.make_response(json.dumps({'code': -1, 'msg': error_code[-1], 'data': e.message}))
