# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request

from .error_code import error_code
from .. import defs

import logging

_logger = logging.getLogger(__name__)


class AddressList(http.Controller):
    @http.route('/<string:sub_domain>/user/shipping-address/list', auth='public', methods=['GET'])
    def get(self, sub_domain, token=None):
        try:
            user = request.env['res.users'].sudo().search([('sub_domain', '=', sub_domain)])
            if not user:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            if not token:
                return request.make_response(json.dumps({'code': 300, 'msg': error_code[300].format('token')}))

            access_token = request.env(user=user.id)['wechat_mall.access_token'].search([
                ('token', '=', token),
                ('create_uid', '=', user.id)
            ])

            if not access_token:
                return request.make_response(json.dumps({'code': 901, 'msg': error_code[901]}))

            wechat_user = request.env(user=user.id)['wechat_mall.user'].search([
                ('open_id', '=', access_token.open_id),
                ('create_uid', '=', user.id)
            ])
            if not wechat_user:
                return request.make_response(json.dumps({'code': 10000, 'msg': error_code[10000]}))

            if not wechat_user.address_ids:
                return request.make_response(json.dumps({'code': 700, 'msg': error_code[700]}))

            response = request.make_response(
                headers={
                    "Content-Type": "json"
                },
                data=json.dumps({
                    "code": 0,
                    "data": [{
                        "address": each_address.address,
                        "areaStr": each_address.district_id.name or '',
                        "cityId": each_address.city_id.id,
                        "cityStr": each_address.city_id.name,
                        "code": each_address.postcode,
                        "dateAdd": each_address.create_date,
                        "dateUpdate": each_address.write_date,
                        "districtId": each_address.district_id.id or False,
                        "id": each_address.id,
                        "isDefault": each_address.is_default,
                        "linkMan": each_address.linkman,
                        "mobile": each_address.phone,
                        "provinceId": each_address.province_id.id,
                        "provinceStr": each_address.province_id.name,
                        "status": 0 if each_address.status else 1,
                        "statusStr": defs.AddressStatus.attrs[each_address.status],
                        "uid": each_address.create_uid.id,
                        "userId": each_address.wechat_user_id.id
                    } for each_address in wechat_user.address_ids.filtered(lambda r: r.status)],
                    "msg": "success"
                })
            )

            return response

        except Exception as e:
            _logger.exception(e)
            return request.make_response(json.dumps({'code': -1, 'msg': error_code[-1], 'data': e.message}))


class AddressAdd(http.Controller):
    @http.route('/<string:sub_domain>/user/shipping-address/add',
                auth='public', methods=['POST'], csrf=False, type='http')
    def post(self, sub_domain, **kwargs):
        try:
            user = request.env['res.users'].sudo().search([('sub_domain', '=', sub_domain)])
            if not user:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            if 'token' not in kwargs.keys():
                return request.make_response(json.dumps({'code': 300, 'msg': error_code[300].format('token')}))

            token = kwargs['token']

            args_key_set = {'address_id', 'province_id', 'city_id', 'district_id',
                            'linkMan', 'address', 'phone', 'postcode', 'is_default'}

            missing_args_key = args_key_set - set(kwargs.keys())
            if missing_args_key:
                return request.make_response(json.dumps({'code': 600, 'msg': error_code[600]}))

            access_token = request.env(user=user.id)['wechat_mall.access_token'].search([
                ('token', '=', token),
                ('create_uid', '=', user.id)
            ])

            if not access_token:
                return request.make_response(json.dumps({'code': 901, 'msg': error_code[901]}))

            wechat_user = request.env(user=user.id)['wechat_mall.user'].search([
                ('open_id', '=', access_token.open_id),
                ('create_uid', '=', user.id)
            ])

            if not wechat_user:
                return request.make_response(json.dumps({'code': 10000, 'msg': error_code[10000]}))

            new_address = request.env(user=user.id)['wechat_mall.address'].create({
                'wechat_user_id': wechat_user.id,
                'linkman': kwargs['linkMan'],
                'phone': kwargs['phone'],
                'province_id': int(kwargs['province_id']),
                'city_id': int(kwargs['city_id']),
                'district_id': int(kwargs['district_id']) if kwargs.get('district_id') else False,
                'address': kwargs['address'],
                'postcode': kwargs['postcode'],
                'is_default': json.loads(kwargs['is_default'])
            })

            address_ids = wechat_user.address_ids.filtered(lambda r: r.id != new_address.id)
            if address_ids:
                address_ids.write({'is_default': False})

            return request.make_response(json.dumps({'code': 0, 'msg': 'success'}))

        except Exception as e:
            _logger.exception(e)
            return request.make_response(json.dumps({'code': -1, 'msg': error_code[-1], 'data': e.message}))


class AddressUpdate(http.Controller):
    @http.route('/<string:sub_domain>/user/shipping-address/update',
                auth='public', methods=['POST'], csrf=False, type='http')
    def post(self, sub_domain, **kwargs):
        try:
            user = request.env['res.users'].sudo().search([('sub_domain', '=', sub_domain)])
            if not user:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            if 'token' not in kwargs.keys():
                return request.make_response(json.dumps({'code': 300, 'msg': error_code[300].format('token')}))

            token = kwargs['token']

            args_key_set = {'address_id', 'is_default'}

            missing_args_key = args_key_set - set(kwargs.keys())
            if missing_args_key:
                return request.make_response(json.dumps({'code': 600, 'msg': error_code[600]}))

            access_token = request.env(user=user.id)['wechat_mall.access_token'].search([
                ('token', '=', token),
                ('create_uid', '=', user.id)
            ])

            if not access_token:
                return request.make_response(json.dumps({'code': 901, 'msg': error_code[901]}))

            wechat_user = request.env(user=user.id)['wechat_mall.user'].search([
                ('open_id', '=', access_token.open_id),
                ('create_uid', '=', user.id)
            ])

            if not wechat_user:
                return request.make_response(json.dumps({'code': 10000, 'msg': error_code[10000]}))

            address = request.env(user=user.id)['wechat_mall.address'].browse(int(kwargs['address_id']))

            if not address:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            address.write({
                'linkman': kwargs['linkman'] if kwargs.get('linkman') else address.linkman,
                'phone': kwargs['phone'] if kwargs.get('phone') else address.phone,
                'province_id': int(kwargs['province_id']) if kwargs.get('province_id') else address.province_id.id,
                'city_id': int(kwargs['city_id']) if kwargs.get('city_id') else address.city_id.id,
                'district_id': int(kwargs['district_id']) if kwargs.get('district_id') else address.district_id.id,
                'address': kwargs['address'] if kwargs.get('address') else address.address,
                'postcode': kwargs['postcode'] if kwargs.get('postcode') else address.postcode,
                'is_default': json.loads(kwargs['is_default'])
            })

            address_ids = wechat_user.address_ids.filtered(lambda r: r.id != address.id)
            if address_ids:
                address_ids.write({'is_default': False})

            return request.make_response(json.dumps({'code': 0, 'msg': 'success'}))

        except Exception as e:
            _logger.exception(e)
            return request.make_response(json.dumps({'code': -1, 'msg': error_code[-1], 'data': e.message}))


class AddressDelete(http.Controller):
    @http.route('/<string:sub_domain>/user/shipping-address/delete', auth='public', methods=['GET'])
    def get(self, sub_domain, token=None, address_id=None, **kwargs):
        try:
            user = request.env['res.users'].sudo().search([('sub_domain', '=', sub_domain)])
            if not user:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            if not token:
                return request.make_response(json.dumps({'code': 300, 'msg': error_code[300].format('token')}))

            if not address_id:
                return request.make_response(json.dumps({'code': 300, 'msg': error_code[300].format('address_id')}))

            access_token = request.env(user=user.id)['wechat_mall.access_token'].search([
                ('token', '=', token),
                ('create_uid', '=', user.id)
            ])

            if not access_token:
                return request.make_response(json.dumps({'code': 901, 'msg': error_code[901]}))

            if not access_token:
                return request.make_response(json.dumps({'code': 901, 'msg': error_code[901]}))

            wechat_user = request.env(user=user.id)['wechat_mall.user'].search([
                ('open_id', '=', access_token.open_id),
                ('create_uid', '=', user.id)
            ])

            if not wechat_user:
                return request.make_response(json.dumps({'code': 10000, 'msg': error_code[10000]}))

            address = request.env(user=user.id)['wechat_mall.address'].browse(int(address_id))

            if not address:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            address.unlink()

            if wechat_user.address_ids:
                wechat_user.address_ids[0].write({'is_default': True})

            return request.make_response(json.dumps({'code': 0, 'msg': 'success'}))

        except Exception as e:
            _logger.exception(e)
            return request.make_response(json.dumps({'code': -1, 'msg': error_code[-1], 'data': e.message}))


class AddressDefault(http.Controller):
    @http.route('/<string:sub_domain>/user/shipping-address/default', auth='public', methods=['GET'])
    def get(self, sub_domain, token=None, **kwargs):
        try:
            user = request.env['res.users'].sudo().search([('sub_domain', '=', sub_domain)])
            if not user:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            if not token:
                return request.make_response(json.dumps({'code': 300, 'msg': error_code[300].format('token')}))

            access_token = request.env(user=user.id)['wechat_mall.access_token'].search([
                ('token', '=', token),
                ('create_uid', '=', user.id)
            ])

            if not access_token:
                return request.make_response(json.dumps({'code': 901, 'msg': error_code[901]}))

            wechat_user = request.env(user=user.id)['wechat_mall.user'].search([
                ('open_id', '=', access_token.open_id),
                ('create_uid', '=', user.id)
            ])

            if not wechat_user:
                return request.make_response(json.dumps({'code': 10000, 'msg': error_code[10000]}))

            address = request.env(user=user.id)['wechat_mall.address'].search([
                ('wechat_user_id', '=', wechat_user.id),
                ('is_default', '=', True)
            ], limit=1)

            if not address:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            response = request.make_response(
                headers={
                    "Content-Type": "json"
                },
                data=json.dumps({
                    "code": 0,
                    "data": {
                        "address": address.address,
                        "areaStr": address.district_id.name or '',
                        "cityId": address.city_id.id,
                        "cityStr": address.city_id.name,
                        "code": address.postcode,
                        "dateAdd": address.create_date,
                        "dateUpdate": address.write_date,
                        "districtId": address.district_id.id or False,
                        "id": address.id,
                        "isDefault": address.is_default,
                        "linkMan": address.linkman,
                        "mobile": address.phone,
                        "provinceId": address.province_id.id,
                        "provinceStr": address.province_id.name,
                        "status": 0 if address.status else 1,
                        "statusStr": defs.AddressStatus.attrs[address.status],
                        "uid": address.create_uid.id,
                        "userId": address.wechat_user_id.id
                    },
                    "msg": "success"
                })
            )

            return response

        except Exception as e:
            _logger.exception(e)
            return request.make_response(json.dumps({'code': -1, 'msg': error_code[-1], 'data': e.message}))


class AddressDetail(http.Controller):
    @http.route('/<string:sub_domain>/user/shipping-address/detail', auth='public', methods=['GET'])
    def get(self, sub_domain, token=None, address_id=None, **kwargs):
        try:
            user = request.env['res.users'].sudo().search([('sub_domain', '=', sub_domain)])
            if not user:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            if not token:
                return request.make_response(json.dumps({'code': 300, 'msg': error_code[300].format('token')}))

            if not address_id:
                return request.make_response(json.dumps({'code': 300, 'msg': error_code[300].format('address_id')}))

            access_token = request.env(user=user.id)['wechat_mall.access_token'].search([
                ('token', '=', token),
                ('create_uid', '=', user.id)
            ])

            if not access_token:
                return request.make_response(json.dumps({'code': 901, 'msg': error_code[901]}))

            address = request.env(user=user.id)['wechat_mall.address'].browse(int(address_id))

            if not address:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            response = request.make_response(
                headers={
                    "Content-Type": "json"
                },
                data=json.dumps({
                    "code": 0,
                    "data": {
                        "address": address.address,
                        "areaStr": address.district_id.name or '',
                        "cityId": address.city_id.id,
                        "cityStr": address.city_id.name,
                        "code": address.postcode,
                        "dateAdd": address.create_date,
                        "dateUpdate": address.write_date,
                        "districtId": address.district_id.id or False,
                        "id": address.id,
                        "isDefault": address.is_default,
                        "linkMan": address.linkman,
                        "mobile": address.phone,
                        "provinceId": address.province_id.id,
                        "provinceStr": address.province_id.name,
                        "status": 0 if address.status else 1,
                        "statusStr": defs.AddressStatus.attrs[address.status],
                        "uid": address.create_uid.id,
                        "userId": address.wechat_user_id.id
                    },
                    "msg": "success"
                })
            )

            return response

        except Exception as e:
            _logger.exception(e)
            return request.make_response(json.dumps({'code': -1, 'msg': error_code[-1], 'data': e.message}))
