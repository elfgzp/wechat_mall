# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ConfigSettings(models.Model):
    _name = 'wechat_mall.config.settings'
    _description = u'基本设置'
    _inherit = 'res.config.settings'

    mall_name = fields.Char('商城名称', help='显示在小程序顶部')

    @api.model
    def default_get(self, fields_list):
        return {field: self.get_config(field) for field in fields_list}

    @api.multi
    def set_default_all(self):
        self.env['ir.values'].set_default('wechat_mall.config.settings', 'mall_name_{uid}'.format(uid=self.env.uid),
                                          self.mall_name)

    def get_config(self, config_name, uid=False, obj=False):
        uid = uid if uid else self.env.uid
        if obj:
            return self.env['ir.values'].search([('name', '=', '{config_name}_{uid}'.format(uid=uid,
                                                                                            config_name=config_name))])
        return self.env['ir.values'].get_default(model=self._name,
                                                 field_name='{config_name}_{uid}'.format(uid=uid,
                                                                                         config_name=config_name))
