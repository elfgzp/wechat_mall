# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Category(models.Model):
    _name = 'wechat_mall.category'
    _description = u'商品分类'

    user_id = fields.Many2one('res.users', string='所属用户')
    name = fields.Char(string='名称')
    category_type = fields.Char(string='类型')
    pid = fields.Many2one('wechat_mall.category', string='上级分类')
    key = fields.Char(string='编号')
    icon = fields.Binary(string='图标')
    level = fields.Integer(string='分类级别')
    is_use = fields.Boolean(string='是否启用')
    sort = fields.Integer(string='排序')
