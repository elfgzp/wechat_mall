# -*- coding: utf-8 -*-

from odoo import models, fields


class Goods(models.Model):
    _name = 'wechat_mall.goods'
    _description = u'商品'

    user_id = fields.Many2one('res.users', string='所属用户')
    subshop_id = fields.Many2one('wechat_mall.subshop', string='所属店铺')
    category_id = fields.Many2one('wechat_mall.category', string='商品分类')
    name = fields.Char('商品名称')
    characteristic = fields.Text('商品特色')
    logistics_id = fields.Many2one('wechat_mall.logistics', string='物流模板')
    sort = fields.Integer('排序')
    recommend_status = fields.Boolean('是否推荐')
    pic = fields.One2many('ir.attachment', 'res_id', string='图片')
    content = fields.Html('详细介绍')
    original_price = fields.Float('原价')
    min_price = fields.Float('最低价')
    stores = fields.Integer('库存')
    number_good_reputation = fields.Integer('好评数')
    number_order = fields.Integer('订单数')
    number_fav = fields.Integer('收藏数')
    views = fields.Integer('浏览量')
