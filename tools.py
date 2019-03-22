# -*- coding: utf-8 -*-

from .weixin.lib.wxcrypt import WXBizDataCrypt
from .weixin import WXAPPAPI
from .weixin.oauth2 import OAuth2AuthExchangeError


def convert_static_link(request, html):
    base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
    return html.replace('src="', 'src="{base_url}'.format(base_url=base_url))


def get_wechat_session_info(app_id, secret, code):
    api = WXAPPAPI(appid=app_id, app_secret=secret)
    try:
        # 使用 code  换取 session key
        session_info = api.exchange_code_for_session_key(code=code)
    except OAuth2AuthExchangeError as e:
        raise e
    return session_info


def get_wechat_user_info(app_id, secret, code, encrypted_data, iv):
    """
    :param app_id: 微信Appid
    :param secret: Secret
    :param code: 调用 wx.login 返回的code
    :param encrypted_data: 加密的用户数据
    :param iv: 解密秘钥
    :return: session_ley, user_info
    """
    session_info = get_wechat_session_info(app_id, secret, code)
    session_key = session_info.get('session_key')
    crypt = WXBizDataCrypt(app_id, session_key)
    # 解密得到 用户信息
    user_info = crypt.decrypt(encrypted_data, iv)
    return session_key, user_info

