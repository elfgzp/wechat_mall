# -*- coding: utf-8 -*-

import json
import xmltodict

from odoo import http, exceptions
from odoo.http import request

from .error_code import error_code
from .. import defs

from weixin.pay import WeixinPay

import logging

_logger = logging.getLogger(__name__)


class MakePayment(http.Controller):
    @http.route('/<string:sub_domain>/pay/wxapp/get-pay-data',
                auth='public', methods=['POST'], csrf=False, type='http')
    def post(self, sub_domain, **kwargs):
        try:
            user = request.env['res.users'].sudo().search([('sub_domain', '=', sub_domain)])
            if not user:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            config = self.env['wechat_mall.config.settings']
            app_id = config.get_config('app_id', uid=user.id)
            wechat_pay_id = config.get_config('wechat_pay_id', uid=user.id)
            wechat_pay_secret = config.get_config('wechat_pay_id', uid=user.id)

            if not app_id:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            if not wechat_pay_id or wechat_pay_secret:
                return request.make_response(json.dumps({'code': 404, 'msg': '未设置wechat_pay_id和wechat_pay_secret'}))

            if 'token' not in kwargs.keys():
                return request.make_response(json.dumps({'code': 300, 'msg': error_code[300].format('token')}))

            token = kwargs.pop('token')

            args_key_set = {'token', 'order_id', 'money'}

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

            wxpay = WeixinPay(appid=app_id, mch_id=wechat_pay_id, partner_key=wechat_pay_secret)

        except Exception as e:
            _logger.exception(e)
            return request.make_response(json.dumps({'code': -1, 'msg': error_code[-1], 'data': e.message}))


class WechatPaymentNotify(http.Controller):
    @http.route('/<string:sub_domain>/pay/notify',
                auth='public', methods=['POST', 'GET'], csrf=False, type='http')
    def post(self, sub_domain, **kwargs):
        try:
            user = request.env['res.users'].sudo().search([('sub_domain', '=', sub_domain)])
            if not user:
                response = request.make_response(
                    headers={
                        "Content-Type": "application/xml"
                    },
                    data=xmltodict.unparse({
                        'xml': {
                            'return_code': 'FAIL',
                            'return_msg': '参数格式校验错误'
                        }
                    })
                )
                return response

            xml_data = request.httprequest.stream.read()
            data = xmltodict.parse(xml_data)['xml']
            if data['return_code'] == 'SUCCESS':
                data.update({'status': defs.PaymentStatus.success})
                payment = request.env(user=user.id)['wechat_mall.payment'].search([
                    ('payment_number', '=', data['out_trade_no'])
                 ])
                payment.write(data)
                payment.order_id.write({'status': defs.OrderStatus.pending})
                mail_template = request.env.ref('wechat_mall.wechat_mall_order_paid')
                mail_template.sudo().send_mail(payment.order_id.id, force_send=True, raise_exception=False)
            else:
                data.update({'status': defs.PaymentStatus.fail})
                payment = request.env(user=user.id)['wechat_mall.payment'].search([
                    ('payment_number', '=', data['out_trade_no'])
                ])
                payment.write(data)

            response = request.make_response(
                headers={
                    "Content-Type": "application/xml"
                },
                data=xmltodict.unparse({
                    'xml': {
                        'return_code': 'SUCCESS',
                        'return_msg': 'SUCCESS'
                    }
                })
            )
            return response

        except Exception as e:
            _logger.exception(e)
            response = request.make_response(
                headers={
                    "Content-Type": "application/xml"
                },
                data=xmltodict.unparse({
                    'xml': {
                        'return_code': 'FAIL',
                        'return_msg': '服务器内部错误'
                    }
                })
            )
            return response
