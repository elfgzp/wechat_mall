# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Banner(models.Model):
    _name = 'wechat_mall.banner'
    _description = u'横幅'

    user_id = fields.Many2one('res.users', string='所属用户')
    type_mark = fields.Integer(string='类型标记(用于扩展)')
    business_id = fields.Integer(string='业务编号')
    title = fields.Char(string='名称', required=True)
    pic = fields.Binary(string='横幅图片', attachment=True)
    link_url = fields.Char(string='链接地址')
    sort = fields.Integer(string='排序')
    remark = fields.Text(string='备注')