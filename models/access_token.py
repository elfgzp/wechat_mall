# -*- coding: utf-8 -*-

import time

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from odoo import models, fields, api, exceptions


class AccessToken(models.TransientModel):
    _name = 'wechat_mall.access_token'
    _description = u'assess token'

    # allow session to survive for 30min in case user is slow
    _transient_max_hours = 2

    token = fields.Char('token', index=True)

    # 调用微信小程序接口
    # https://api.weixin.qq.com/sns/jscode2session?appid=APPID&secret=SECRET&js_code=JSCODE&grant_type=authorization_code
    # 返回的session_key, open_id

    session_key = fields.Char('session_key', required=True)
    open_id = fields.Char('open_id', required=True)

    @api.model
    def create(self, vals):
        record = super(AccessToken, self).create(vals)
        record.write({'token': record.generate_token()})
        return record

    def generate_token(self):
        config = self.env['wechat_mall.config.settings']
        secret_key = config.get_config('secret', self.create_uid.id)
        app_id = config.get_config('app_id', self.create_uid.id)
        if not secret_key or not app_id:
            raise exceptions.ValidationError('该用户的商城未设置secret_key或appId 无法生成token!')

        s = Serializer(
            secret_key=secret_key,
            salt=app_id,
            expires_in=AccessToken._transient_max_hours * 3600)
        timestamp = time.time()
        return s.dumps({'session_key': self.session_key,
                        'open_id': self.open_id,
                        'iat': timestamp})
