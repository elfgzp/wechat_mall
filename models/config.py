# -*- coding: utf-8 -*-

from odoo import models, fields, api

from custom_model import CustomModel


class ConfigSettingWizard(models.TransientModel):
    _name = 'wechat_mall.config.settings'
    _description = u'基本设置'

    sub_domain = fields.Char('小程序接口子域名', help='用于小程序接口', readonly=True,
                             default=lambda self: self.env.user.sub_domain)

    mall_name = fields.Char('商城名称', help='显示在小程序顶部')
    app_id = fields.Char('appid')
    secret = fields.Char('secret')
    wechat_pay_id = fields.Char('微信支付商户号')
    wechat_pay_secret = fields.Char('微信支付商户秘钥')

    kdniao_app_id = fields.Char('快递鸟商户ID')
    kdniao_app_key = fields.Char('快递鸟API key')

    @api.multi
    def cancel(self):
        # ignore the current record, and send the action to reopen the view
        actions = self.env['ir.actions.act_window'].search([('res_model', '=', self._name)], limit=1)
        if actions:
            return actions.read()[0]
        return {}

    @api.multi
    def execute(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @api.model
    def default_get(self, fields_list):
        config = self.env['wechat_mall.config'].search([('create_uid', '=', self.env.uid)])
        result = super(ConfigSettingWizard, self).default_get(fields_list)
        if config:
            config.ensure_one()
            result.update({
                f: config.__getattribute__(f) if not isinstance(config.__getattribute__(f), models.Model)
                else config.get_relative_field_val(f)
                for f in fields_list if f not in result.keys()})
            return result
        else:
            return result

    @api.model
    def create(self, vals):
        config = self.env['wechat_mall.config'].search([('create_uid', '=', self.env.uid)])
        if config:
            config.ensure_one()
            config.write(vals)
        else:
            config.create(vals)

        return super(ConfigSettingWizard, self).create(vals)

    def get_config(self, key, uid=False, obj=False):
        uid = uid if uid else self.env.uid
        config = self.env['wechat_mall.config'].search([('create_uid', '=', uid)])
        if obj:
            return config

        if config:
            config.ensure_one()
            return config.__getattribute__(key) if not isinstance(config.__getattribute__(key), models.Model) \
                else config.get_relative_field_val(key)
        else:
            return False


class ConfigSettings(CustomModel, models.Model):
    _name = 'wechat_mall.config'
    _description = u'基本设置'

    mall_name = fields.Char('商城名称', help='显示在小程序顶部')
    app_id = fields.Char('appid')
    secret = fields.Char('secret')
    wechat_pay_id = fields.Char('微信支付商户号')
    wechat_pay_secret = fields.Char('微信支付商户秘钥')

    kdniao_app_id = fields.Char('快递鸟商户ID')
    kdniao_app_key = fields.Char('快递鸟API key')
