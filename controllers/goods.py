# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request

from .error_code import error_code
from .. import defs
from ..tools import convert_static_link


class GoodsList(http.Controller):
    @http.route('/<model("res.users"):user>/shop/goods/list', auth='public', methods=['GET'])
    def get(self, user, category_id=False):
        try:
            goods_list = request.env['wechat_mall.goods'].search(
                [('create_uid', '=', user.id),
                 ('status', '=', True),
                 ('category_id', '=', int(category_id))]
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
            return request.make_response(json.dumps({'code': -1, 'msg': error_code[-1], 'data': e.message}))


class GoodsDetail(http.Controller):
    @http.route('/<model("res.users"):user>/shop/goods/detail', auth='public', methods=['GET'])
    def get(self, user, goods_id=False):
        try:
            if not goods_id:
                return request.make_response(json.dumps({'code': 300, 'msg': error_code[300].format('goods_id')}))

            goods = request.env['wechat_mall.goods'].browse(int(goods_id))

            if not goods:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            if goods.create_uid.id != user.id or not goods.status:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            response = request.make_response(
                headers={
                    "Content-Type": "json"
                },
                data=json.dumps({
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
                        "content": convert_static_link(request, goods.content) if goods.content else '',
                        "properties": [
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
                        ],
                        "basicInfo": {
                            "categoryId": goods.category_id.id,
                            "characteristic": goods.characteristic or '',
                            "dateAdd": goods.create_date,
                            "dateUpdate": goods.write_date,
                            "id": goods.id,
                            "logisticsId": goods.logistics_id.id,
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
                })
            )

            goods.sudo().write({'views': goods.views + 1})

            return response

        except Exception as e:
            return request.make_response(json.dumps({'code': -1, 'msg': error_code[-1], 'data': e.message}))


class GoodPrice(http.Controller):
    @http.route('/<model("res.users"):user>/shop/goods/price', auth='public', methods=['GET'])
    def get(self, user, goods_id=False, property_child_ids=False):
        try:
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
            return request.make_response(json.dumps({'code': -1, 'msg': error_code[-1], 'data': e.message}))
