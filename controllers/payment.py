# -*- coding: utf-8 -*-

import time
import json
import xmltodict

from odoo import http, exceptions
from odoo.http import request

from .error_code import error_code
from .. import defs

from ..weixin.pay import WeixinPay
from ..weixin.helper import md5_constructor as md5

import logging

_logger = logging.getLogger(__name__)


def build_pay_sign(app_id, nonce_str, prepay_id, time_stamp, key, signType='MD5'):
    """
    :param app_id:
    :param nonce_str:
    :param prepay_id:
    :param time_stamp:
    :param key:
    :param signType:
    :return:
    """
    sign = 'appId={app_id}' \
           '&nonceStr={nonce_str}' \
           '&package=prepay_id={prepay_id}' \
           '&signType={signType}' \
           '&timeStamp={time_stamp}' \
           '&key={key}'.format(app_id=app_id, nonce_str=nonce_str, prepay_id=prepay_id,
                               time_stamp=time_stamp, key=key, signType=signType)
    return md5(sign).hexdigest().upper()


class MakePayment(http.Controller):
    @http.route('/<string:sub_domain>/pay/wxapp/get-pay-data',
                auth='public', methods=['POST'], csrf=False, type='http')
    def post(self, sub_domain, **kwargs):
        try:
            user = request.env['res.users'].sudo().search([('sub_domain', '=', sub_domain)])
            if not user:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            config = request.env(user=user.id)['wechat_mall.config.settings']
            app_id = config.get_config('app_id', uid=user.id)
            wechat_pay_id = config.get_config('wechat_pay_id', uid=user.id)
            wechat_pay_secret = config.get_config('wechat_pay_secret', uid=user.id)

            if not app_id:
                return request.make_response(json.dumps({'code': 404, 'msg': error_code[404]}))

            if not wechat_pay_id or not wechat_pay_secret:
                return request.make_response(json.dumps({'code': 404, 'msg': '未设置wechat_pay_id和wechat_pay_secret'}))

            if 'token' not in kwargs.keys():
                return request.make_response(json.dumps({'code': 300, 'msg': error_code[300].format('token')}))

            token = kwargs.pop('token')

            args_key_set = {'order_id', 'money'}

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

            payment = request.env(user=user.id)['wechat_mall.payment'].create({
                'order_id': int(kwargs['order_id']),
                'wechat_user_id': wechat_user.id,
                'price': float(kwargs['money'])
            })

            mall_name = config.get_config('mall_name', uid=user.id) or '微信小程序商城'
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            wxpay = WeixinPay(appid=app_id, mch_id=wechat_pay_id, partner_key=wechat_pay_secret)
            unified_order = wxpay.unifiedorder(
                body=u'{mall_name}'.format(mall_name=mall_name),
                total_fee=int(float(kwargs['money']) * 100),
                notify_url=u'{base_url}/{sub_domain}/pay/notify'.format(base_url=base_url, sub_domain=sub_domain),
                openid=u'{}'.format(wechat_user.open_id),
                out_trade_no=u'{}'.format(payment.order_id.order_num)

            )
            if unified_order['return_code'] == 'SUCCESS' and not unified_order['result_code'] == 'FAIL':
                time_stamp = str(int(time.time()))
                response = request.make_response(
                    headers={
                        "Content-Type": "json"
                    },
                    data=json.dumps({
                        "code": 0,
                        "data": {
                            'timeStamp': str(int(time.time())),
                            'nonceStr': unified_order['nonce_str'],
                            'prepayId': unified_order['prepay_id'],
                            'sign': build_pay_sign(app_id, unified_order['nonce_str'], unified_order['prepay_id'],
                                                   time_stamp, wechat_pay_secret)
                        },
                        "msg": "success"
                    })
                )
            else:
                if unified_order['err_code'] == 'ORDERPAID':
                    order = payment.order_id
                    order.write({'status': 'pending'})
                    mail_template = request.env.ref('wechat_mall.wechat_mall_order_paid')
                    mail_template.sudo().send_mail(order.id, force_send=True, raise_exception=False)
                    payment.sudo().unlink()
                return request.make_response(
                    json.dumps({'code': -1, 'msg': unified_order.get('err_code_des', unified_order['return_msg'])})
                )

            return response
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
                            u'return_code': 'FAIL',
                            u'return_msg': '参数格式校验错误'
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
                        'return_code': u'SUCCESS',
                        'return_msg': u'SUCCESS'
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
                        'return_code': u'FAIL',
                        'return_msg': u'服务器内部错误'
                    }
                })
            )
            return response
