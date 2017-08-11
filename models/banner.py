# -*- coding: utf-8 -*-

from odoo import models, fields, api

from .. import defs


class Banner(models.Model):
    _name = 'wechat_mall.banner'
    _description = u'横幅'
    _rec_name = 'title'
    _order = 'sort'

    type_mark = fields.Integer(string='类型标记(用于扩展)')
    business_id = fields.Integer(string='业务编号')
    title = fields.Char(string='名称', required=True)
    pic = fields.Many2one('ir.attachment', string='图片')
    link_url = fields.Char(string='链接地址')
    sort = fields.Integer(string='排序')
    status = fields.Boolean('显示', default=True, required=True)
    remark = fields.Text(string='备注')
