# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request
from odoo import fields

from .. import defs
from .error_code import error_code
from ..tools import get_wechat_session_info, get_wechat_user_info

import logging

_logger = logging.getLogger(__name__)


class WechatUserCheckToken(http.Controller):
    @http.route('/<string:sub_domain>/user/check-token', auth='public', methods=['GET'])
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

            return request.make_response(json.dumps({'code': 0, 'msg': 'success'}))

        except Exception as e:
            _logger.exception(e)
            return request.make_response(json.dumps({'code': -1, 'msg': error_code[-1], 'data': e.message}))


class WeChatUserLogin(http.Controller):
    @http.route('/<string:sub_domain>/user/wxapp/login', auth='public', methods=['GET'])
    def get(self, sub_domain, code=None, **kwargs):
        try:
            user = request.env['res.users'].sudo().search([('sub_domain', '=', sub_domain)])
            if not user:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            config = request.env['wechat_mall.config.settings']

            if not code:
                return request.make_response(json.dumps({'code': 300, 'msg': error_code[300].format('code')}))

            app_id = config.get_config('app_id', uid=user.id)
            secret = config.get_config('secret', uid=user.id)

            if not app_id or not secret:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            session_info = get_wechat_session_info(app_id, secret, code)
            if session_info.get('errcode'):
                return request.make_response(
                    json.dumps({'code': -1, 'msg': error_code[-1], 'data': session_info.get('errmsg')})
                )

            open_id = session_info['openid']
            wechat_user = request.env(user=user.id)['wechat_mall.user'].search([
                ('open_id', '=', open_id),
                ('create_uid', '=', user.id)
            ])
            if not wechat_user:
                return request.make_response(json.dumps({'code': 10000, 'msg': error_code[10000]}))

            wechat_user.write({'last_login': fields.Datetime.now(), 'ip': request.httprequest.remote_addr})
            access_token = request.env(user=user.id)['wechat_mall.access_token'].search([
                ('open_id', '=', open_id),
                ('create_uid', '=', user.id)
            ])

            if not access_token:
                session_key = session_info['session_key']
                access_token = request.env(user=user.id)['wechat_mall.access_token'].create({
                    'open_id': open_id,
                    'session_key': session_key,
                })

            response = request.make_response(
                headers={
                    "Content-Type": "json"
                },
                data=json.dumps({
                    'code': 0,
                    'token': access_token.token
                })
            )

            return response

        except AttributeError:
            return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

        except Exception as e:
            _logger.exception(e)
            return request.make_response(json.dumps({'code': -1, 'msg': error_code[-1], 'data': e.message}))


class WeChatUserRegisterComplex(http.Controller):
    @http.route('/<string:sub_domain>/user/wxapp/register/complex', auth='public', methods=['GET'])
    def get(self, sub_domain, code=None, encrypted_data=None, iv=None, **kwargs):
        try:
            user = request.env['res.users'].sudo().search([('sub_domain', '=', sub_domain)])
            if not user:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            config = request.env['wechat_mall.config.settings']

            if not code:
                return request.make_response(json.dumps({'code': 300, 'msg': error_code[300].format('code')}))

            if not encrypted_data:
                return request.make_response(json.dumps({'code': 300, 'msg': error_code[300].format('encrypted_data')}))

            if not iv:
                return request.make_response(json.dumps({'code': 300, 'msg': error_code[300].format('iv')}))

            app_id = config.get_config('app_id', uid=user.id)
            secret = config.get_config('secret', uid=user.id)

            if not app_id or not secret:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            session_key, user_info = get_wechat_user_info(app_id, secret, code, encrypted_data, iv)
            request.env(user=user.id)['wechat_mall.user'].create({
                'name': user_info['nickName'],
                'open_id': user_info['openId'],
                'gender': user_info['gender'],
                'language': user_info['language'],
                'country': user_info['country'],
                'province': user_info['province'],
                'city': user_info['city'],
                'avatar_url': user_info['avatarUrl'],
                'register_ip': request.httprequest.remote_addr,
            })

            return request.make_response(json.dumps({'code': 0, 'msg': 'success'}))

        except AttributeError:
            return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

        except Exception as e:
            _logger.exception(e)
            return request.make_response(json.dumps({'code': -1, 'msg': error_code[-1], 'data': e.message}))
