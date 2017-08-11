# -*- coding: utf-8 -*-

from odoo import models, fields


class Goods(models.Model):
    _name = 'wechat_mall.goods'
    _description = u'商品'

    subshop_id = fields.Many2one('wechat_mall.subshop', string='所属店铺')
    category_id = fields.Many2one('wechat_mall.category', string='商品分类', required=True)
    name = fields.Char('商品名称')
    characteristic = fields.Text('商品特色')
    logistics_id = fields.Many2one('wechat_mall.logistics', string='物流模板')
    sort = fields.Integer('排序', default=0)
    recommend_status = fields.Boolean('是否推荐')
    status = fields.Boolean('是否上架')
    pic = fields.One2many('ir.attachment', 'res_id', string='图片')
    content = fields.Html('详细介绍')
    property_ids = fields.Many2many('wechat_mall.goods.property', 'good_ids', string='商品规格')
    original_price = fields.Float('原价', default=0, required=True)
    min_price = fields.Float('最低价', default=0, required=True)
    stores = fields.Integer('库存', default=0, required=True)
    number_good_reputation = fields.Integer('好评数', default=0, required=True)
    number_order = fields.Integer('订单数', default=0, required=True)
    number_fav = fields.Integer('收藏数', default=0, required=True)
    views = fields.Integer('浏览量', default=0, required=True)
    weight = fields.Float(default=0, required=True)


class Property(models.Model):
    _name = 'wechat_mall.goods.property'
    _description = u'商品规格'

    name = fields.Char('规格名称', required=True)
    goods_ids = fields.Many2many('wechat_mall.goods', 'property_ids', string='关联商品')
    child_ids = fields.One2many('wechat_mall.goods.property_child', 'property_id', string='子属性')
    sort = fields.Integer('排序', default=0)


class PropertyChild(models.Model):
    _name = 'wechat_mall.goods.property_child'
    _description = u'商品规格子属性'

    name = fields.Char('规格子属性名称', required=True)
    property_id = fields.Many2one('wechat_mall.goods.property', string='商品规格', required=True)
    original_price = fields.Float('原始价格', default=0, required=True)
    price = fields.Float('现价', default=0, required=True)
    stores = fields.Integer('库存', default=0, required=True)
    sort = fields.Integer('排序', default=0)
    remark = fields.Char('备注')
