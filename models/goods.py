# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class Goods(models.Model):
    _name = 'wechat_mall.goods'
    _description = u'商品'
    _order = 'sort'

    subshop_id = fields.Many2one('wechat_mall.subshop', string='所属店铺')
    category_id = fields.Many2one('wechat_mall.category', string='商品分类', ondelete='set null')
    name = fields.Char('商品名称')
    characteristic = fields.Text('商品特色')
    logistics_id = fields.Many2one('wechat_mall.logistics', string='物流模板', required=True)
    sort = fields.Integer('排序', default=0)
    recommend_status = fields.Boolean('是否推荐')
    status = fields.Boolean('是否上架')
    pic = fields.Many2many('ir.attachment', string='图片')
    content = fields.Html('详细介绍')
    property_ids = fields.Many2many('wechat_mall.goods.property', 'goods_id', string='商品规格')
    price_ids = fields.One2many('wechat_mall.goods.property_child.price', 'goods_id', string='商品不同规格价格',
                                compute='_compute_property_ids', readonly=False, store=True)
    original_price = fields.Float('原价', default=0, required=True)
    min_price = fields.Float('最低价', default=0, required=True)
    stores = fields.Integer('库存', default=0, required=True)
    number_good_reputation = fields.Integer('好评数', default=0, required=True)
    number_order = fields.Integer('订单数', default=0, required=True)
    number_fav = fields.Integer('收藏数', default=0, required=True)
    views = fields.Integer('浏览量', default=0, required=True)
    weight = fields.Float(default=0, required=True)

    @api.multi
    def write(self, vals):
        if 'price_ids' in vals.keys() and self.price_ids:
            price_ids = self.env['wechat_mall.goods.property_child.price'].search([
                ('id', 'in', [each[1] for each in vals['price_ids']])
            ])
            vals['price_ids'] = [each for each in vals['price_ids'] if each[1] in price_ids.ids + [0]]
            if not vals['price_ids']:
                vals.pop('price_ids')

        result = super(Goods, self.with_context(
            {'recompute': self._context.get('recompute', False), 'goods_id': self.id})).write(vals)

        self.env['wechat_mall.goods.property_child.price'].search([('goods_id', '=', False)]).unlink()
        return result

    @api.depends('property_ids')
    @api.onchange('property_ids')
    def _compute_property_ids(self):
        self.ensure_one()
        self.price_ids = self._price_ids()

    def _price_ids(self):
        price_ids = self.env['wechat_mall.goods.property_child.price']
        property_list = []
        for property_id in self.property_ids.sorted(lambda r: r.sort):
            if property_id.child_ids:
                property_list.append(['{}:{},'.format(property_id.id, child_id.id)
                                      for child_id in property_id.child_ids])
        property_child_ids_list = []
        while len(property_list) >= 1:
            property_child_ids_list = property_list.pop(0)
            if property_list:
                top_property = property_list.pop(0)
                property_child_ids_list = [head + tail for head in property_child_ids_list for tail in top_property]

        for each_property_child_ids in property_child_ids_list:
            price_id = price_ids.with_context({'recompute': False}).create({
                'property_child_ids': each_property_child_ids,
            })

            price_ids |= price_id

        return price_ids


class Property(models.Model):
    _name = 'wechat_mall.goods.property'
    _description = u'商品规格'
    _order = 'sort'

    name = fields.Char('规格名称', required=True)
    goods_ids = fields.Many2many('wechat_mall.goods', 'property_ids', string='关联商品')
    child_ids = fields.One2many('wechat_mall.goods.property_child', 'property_id', string='子属性')
    sort = fields.Integer('排序', default=0)

    @api.multi
    def write(self, vals):
        try:
            for each_record in self:
                if 'sort' in vals.keys() and vals.get('sort') != each_record.sort:
                    each_record._write(vals)
                    goods_ids = self.env['wechat_mall.goods'].with_context({'recompute': True}).browse(
                        each_record._goods_ids())
                    if goods_ids:
                        for goods_id in goods_ids:
                            goods_id.write({'price_ids': [(6, 0, goods_id._price_ids().ids)]})
                else:
                    each_record._write(vals)

        except Exception as e:
            raise exceptions.ValidationError(e)
        else:
            return True

    def _goods_ids(self):
        self.env.cr.execute("""
            SELECT 
                wechat_mall_goods_property_id,
                array_agg(wechat_mall_goods_id)
            FROM 
                wechat_mall_goods_wechat_mall_goods_property_rel
            WHERE wechat_mall_goods_property_id = {}
            GROUP BY wechat_mall_goods_property_id
        """.format(self.id))

        result = self.env.cr.fetchone()
        return result[1] if result else None


class PropertyChild(models.Model):
    _name = 'wechat_mall.goods.property_child'
    _description = u'商品规格子属性'
    _order = 'sort'

    name = fields.Char('规格子属性名称', required=True)
    property_id = fields.Many2one('wechat_mall.goods.property', string='商品规格', required=True)
    sort = fields.Integer('排序', default=0)
    remark = fields.Char('备注')


class PropertyChildPrice(models.Model):
    _name = 'wechat_mall.goods.property_child.price'
    _description = u'商品不同规格价格'

    name = fields.Char('规格名称', compute='_compute_name')
    goods_id = fields.Many2one('wechat_mall.goods', string='关联商品', ondelete='cascade')

    property_child_ids = fields.Char('商品规格', index=1, required=True)
    # 拼接字符'property_id1:child_id1,property_id2:child_id2,'

    original_price = fields.Float('原始价格', default=0, required=True)
    price = fields.Float('现价', default=0, required=True)
    stores = fields.Integer('库存', default=0, required=True)

    @api.model
    def create(self, vals):
        return super(PropertyChildPrice, self).create(vals)

    @api.multi
    def write(self, vals):
        goods_id = self._context.get('goods_id')
        if goods_id:
            vals['goods_id'] = goods_id

        result = super(PropertyChildPrice, self).write(vals)
        return result

    @api.multi
    @api.depends('property_child_ids')
    def _compute_name(self):
        for each_record in self:
            property_child_list = [(int(property_child.split(':')[0]), int(property_child.split(':')[1]))
                                   for property_child in each_record.property_child_ids.split(',') if property_child]

            name = ''
            for property_child_tuple in property_child_list:
                if not name:
                    name = '{}({})'.format(
                        self.env['wechat_mall.goods.property'].browse(property_child_tuple[0]).name,
                        self.env['wechat_mall.goods.property_child'].browse(property_child_tuple[1]).name)
                else:
                    name += ' - {}({})'.format(
                        self.env['wechat_mall.goods.property'].browse(property_child_tuple[0]).name,
                        self.env['wechat_mall.goods.property_child'].browse(property_child_tuple[1]).name)

            each_record.name = name
