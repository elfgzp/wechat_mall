# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request

from .error_code import error_code
from .. import defs
from ..tools import convert_static_link

import logging

_logger = logging.getLogger(__name__)


class GoodsList(http.Controller):
    @http.route('/<string:sub_domain>/shop/goods/list', auth='public', methods=['GET'])
    def get(self, sub_domain, category_id=False, **kwargs):
        try:
            user = request.env['res.users'].sudo().search([('sub_domain', '=', sub_domain)])
            if not user:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            goods_list = request.env['wechat_mall.goods'].search(
                [('create_uid', '=', user.id),
                 ('status', '=', True),
                 ('category_id', 'in',
                  [int(category_id)] + request.env['wechat_mall.category'].browse(int(category_id)).child_ids.ids)]
                if category_id else [('create_uid', '=', user.id), ('status', '=', True)])

            if not goods_list:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            response = request.make_response(
                headers={
                    "Content-Type": "json"
                },
                data=json.dumps({
                    "code": 0,
                    "data": [
                        {
                            "categoryId": each_goods.category_id.id,
                            "characteristic": each_goods.characteristic,
                            "dateAdd": each_goods.create_date,
                            "dateUpdate": each_goods.write_date,
                            "id": each_goods.id,
                            "logisticsId": each_goods.logistics_id.id,
                            "minPrice": each_goods.min_price,
                            "name": each_goods.name,
                            "numberFav": each_goods.number_fav,
                            "numberGoodReputation": each_goods.number_good_reputation,
                            "numberOrders": each_goods.number_order,
                            "originalPrice": each_goods.original_price,
                            "paixu": each_goods.sort or 0,
                            "pic": each_goods.pic[0].static_link() if each_goods.pic else '',
                            "recommendStatus": 0 if not each_goods.recommend_status else 1,
                            "recommendStatusStr": defs.GoodsRecommendStatus.attrs[each_goods.recommend_status],
                            "shopId": each_goods.subshop_id.id if each_goods.subshop_id else 0,
                            "status": 0 if each_goods.status else 1,
                            "statusStr": defs.GoodsStatus.attrs[each_goods.status],
                            "stores": each_goods.stores,
                            "userId": each_goods.create_uid.id,
                            "views": each_goods.views,
                            "weight": each_goods.weight
                        } for each_goods in goods_list
                    ],
                    "msg": "success"
                })
            )

            return response

        except Exception as e:
            _logger.exception(e)
            return request.make_response(json.dumps({'code': -1, 'msg': error_code[-1], 'data': e.message}))


class GoodsDetail(http.Controller):
    @http.route('/<string:sub_domain>/shop/goods/detail', auth='public', methods=['GET'])
    def get(self, sub_domain, goods_id=False, **kwargs):
        try:
            user = request.env['res.users'].sudo().search([('sub_domain', '=', sub_domain)])
            if not user:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            if not goods_id:
                return request.make_response(json.dumps({'code': 300, 'msg': error_code[300].format('goods_id')}))

            goods = request.env['wechat_mall.goods'].browse(int(goods_id))

            if not goods:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            if goods.create_uid.id != user.id or not goods.status:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            data = {
                "code": 0,
                "data": {
                    "category": {
                        "dateAdd": goods.category_id.create_date,
                        "dateUpdate": goods.category_id.write_date,
                        "icon": goods.category_id.icon.static_link() if goods.category_id.icon else '',
                        "id": goods.category_id.id,
                        "isUse": goods.category_id.is_use,
                        "key": goods.category_id.key,
                        "name": goods.category_id.name,
                        "paixu": goods.category_id.sort or 0,
                        "pid": goods.category_id.pid.id if goods.category_id.pid else 0,
                        "type": goods.category_id.category_type,
                        "userId": goods.category_id.create_uid.id
                    },
                    "pics": [
                        {
                            "goodsId": goods.id,
                            "id": each_pic.id,
                            "pic": each_pic.static_link()
                        } for each_pic in goods.pic
                    ],
                    "logistics": {
                        "logisticsBySelf": goods.logistics_id.by_self,
                        "isFree": goods.logistics_id.free,
                        "by_self": goods.logistics_id.by_self,
                        "feeType": defs.LogisticsValuationResponseType.attrs[goods.logistics_id.valuation_type],
                        "feeTypeStr": defs.LogisticsValuationType.attrs[goods.logistics_id.valuation_type],
                        "details": [
                            {
                                "addAmount": each_transportation.increase_price,
                                "addNumber": each_transportation.increase_amount,
                                "firstAmount": each_transportation.less_price,
                                "firstNumber": each_transportation.less_amount,
                                "type": defs.TransportResponseType.attrs[each_transportation.transport_type]
                            } for each_transportation in goods.logistics_id.transportation_ids
                        ]
                    },
                    "content": convert_static_link(request, goods.content) if goods.content else '',
                    "basicInfo": {
                        "categoryId": goods.category_id.id,
                        "characteristic": goods.characteristic or '',
                        "dateAdd": goods.create_date,
                        "dateUpdate": goods.write_date,
                        "id": goods.id,
                        "logisticsId": goods.logistics_id.id or 0,
                        "minPrice": goods.min_price,
                        "name": goods.name,
                        "numberFav": goods.number_fav,
                        "numberGoodReputation": goods.number_good_reputation,
                        "numberOrders": goods.number_order,
                        "originalPrice": goods.original_price,
                        "paixu": goods.sort or 0,
                        "pic": goods.pic[0].static_link() if goods.pic else '',
                        "recommendStatus": 0 if not goods.recommend_status else 1,
                        "recommendStatusStr": defs.GoodsRecommendStatus.attrs[goods.recommend_status],
                        "shopId": goods.subshop_id.id if goods.subshop_id else 0,
                        "status": 0 if goods.status else 1,
                        "statusStr": defs.GoodsStatus.attrs[goods.status],
                        "stores": goods.stores,
                        "userId": goods.create_uid.id,
                        "views": goods.views,
                        "weight": goods.weight
                    }
                },
                "msg": "success"
            }
            if goods.property_ids:
                data["data"]["properties"] = [
                    {
                        "childsCurGoods": [
                            {
                                "dateAdd": each_child.create_date,
                                "dateUpdate": each_child.write_date,
                                "id": each_child.id,
                                "name": each_child.name,
                                "paixu": each_child.sort,
                                "propertyId": each_property.id,
                                "remark": each_child.remark or '',
                                "userId": each_child.create_uid.id
                            } for each_child in each_property.child_ids
                        ],
                        "dateAdd": each_property.create_date,
                        "dateUpdate": each_property.write_date,
                        "id": each_property.id,
                        "name": each_property.name,
                        "paixu": each_property.sort or 0,
                        "userId": each_property.create_uid.id
                    } for each_property in goods.property_ids if each_property.child_ids
                ]

            response = request.make_response(
                headers={
                    "Content-Type": "json"
                },
                data=json.dumps(data)
            )

            goods.sudo().write({'views': goods.views + 1})

            return response

        except Exception as e:
            _logger.exception(e)
            return request.make_response(json.dumps({'code': -1, 'msg': error_code[-1], 'data': e.message}))


class GoodsPrice(http.Controller):
    @http.route('/<string:sub_domain>/shop/goods/price', auth='public', methods=['GET'])
    def get(self, sub_domain, goods_id=False, property_child_ids=False, **kwargs):
        try:
            user = request.env['res.users'].sudo().search([('sub_domain', '=', sub_domain)])
            if not user:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            if not goods_id:
                return request.make_response(json.dumps({'code': 300, 'msg': error_code[300].format('goods_id')}))

            if not property_child_ids:
                return request.make_response(
                    json.dumps({'code': 300, 'msg': error_code[300].format('property_child_ids')}))

            goods = request.env['wechat_mall.goods'].browse(int(goods_id))

            if not goods:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            if goods.create_uid.id != user.id:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            price = request.env['wechat_mall.goods.property_child.price'].search([
                ('goods_id', '=', goods.id),
                ('property_child_ids', '=', property_child_ids)
            ])

            if not price:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            response = request.make_response(
                headers={
                    "Content-Type": "json"
                },
                data=json.dumps({
                    "code": 0,
                    "data": {
                        "goodsId": goods.id,
                        "id": price.id,
                        "originalPrice": price.original_price,
                        "price": price.price,
                        "propertyChildIds": price.property_child_ids,
                        "stores": price.stores
                    },
                    "msg": "success"
                })
            )

            return response

        except Exception as e:
            _logger.exception(e)
            return request.make_response(json.dumps({'code': -1, 'msg': error_code[-1], 'data': e.message}))


class GoodsPriceFreight(http.Controller):
    @http.route('/<string:sub_domain>/shop/goods/price/freight', auth='public', methods=['GET'])
    def get(self, sub_domain, **kwargs):
        try:
            user = request.env['res.users'].sudo().search([('sub_domain', '=', sub_domain)])
            if not user:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            args_key_set = {'logistics_id', 'transport_type', 'province_id', 'city_id', 'district_id'}

            missing_args_key = args_key_set - set(kwargs.keys())
            if missing_args_key:
                return request.make_response(
                    json.dumps({'code': 300, 'msg': error_code[300].format(','.join(missing_args_key))}))

            # 使用order保证运输费是最精确的地址匹配
            transport = request.env(user=user.id)['wechat_mall.district.transportation'].search([
                ('create_uid', '=', user.id),
                ('default_transportation_id.logistics_id', '=', int(kwargs['logistics_id'])),
                ('default_transportation_id.transport_type', '=',
                 defs.TransportRequestType.attrs[int(kwargs.get('transport_type'))]),
                ('province_id', '=', int(kwargs['province_id'])),
                ('city_id', '=', int(kwargs['city_id'])),
                ('district_id', 'in', [int(kwargs['district_id']) if kwargs['district_id'] else False, False]),
            ], limit=1, order='district_id asc')

            if not transport:
                transport = request.env(user=user.id)['wechat_mall.transportation'].search([
                    ('create_uid', '=', user.id),
                    ('logistics_id', '=', int(kwargs['logistics_id'])),
                    ('transport_type', '=', defs.TransportRequestType.attrs[int(kwargs.get('transport_type'))]),
                ], limit=1)

            response = request.make_response(
                headers={
                    "Content-Type": "json"
                },
                data=json.dumps({
                    "code": 0,
                    "data": {
                        "transport_type": int(kwargs.get('transport_type')),
                        "firstNumber": transport.less_amount or 0,
                        "addAmount": transport.increase_price or 0,
                        "firstAmount": transport.less_price or 0,
                        "addNumber": transport.increase_amount or 0,
                    },
                    "msg": "success"
                })
            )

            return response

        except Exception as e:
            _logger.exception(e)
            return request.make_response(json.dumps({'code': -1, 'msg': error_code[-1], 'data': e.message}))
