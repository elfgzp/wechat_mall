# -*- coding: utf-8 -*-

from odoo import models, fields, api

from .. import defs


class Order(models.Model):
    _name = 'wechat_mall.order'
    _description = u'订单'
    _inherit = ['mail.thread']
    _rec_name = 'order_num'

    wechat_user_id = fields.Many2one('wechat_mall.user', string='微信用户')
    order_num = fields.Char('订单号', index=True)
    goods_ids = fields.Many2many('wechat_mall.goods', string='商品', help='真实商品数据，保留便于查询。')
    order_goods_ids = fields.One2many('wechat_mall.order.goods', 'order_id',
                                      string='订单商品', help='商品参数数据冗余，防止商品修改或删除。')
    number_goods = fields.Integer('商品数量')
    goods_price = fields.Float('商品总金额', requried=True, default=0)
    logistics_price = fields.Float('物流费用', requried=True, default=0)
    total = fields.Float('实际支付', requried=True, default=0, track_visibility='onchange')
    status = fields.Selection(defs.OrderStatus.attrs.items(), default=defs.OrderStatus.unpaid,
                              required=True, string='状态', track_visibility='onchange')

    remark = fields.Char('备注')
    linkman = fields.Char('联系人')
    phone = fields.Char('手机号码')
    province_id = fields.Many2one('wechat_mall.province', string='省', required=True)
    city_id = fields.Many2one('wechat_mall.city', string='市', required=True)
    district_id = fields.Many2one('wechat_mall.district', string='区')
    address = fields.Char('详细地址')
    postcode = fields.Char('邮政编码', requried=True)

    @api.model
    def create(self, vals):
        vals['order_num'] = self.env['ir.sequence'].next_by_code('wechat_mall.order_num')
        return super(Order, self).create(vals)

    def make_order(self, goods_json_str, remark, province_id, city_id, address,
                   link_man, phone, postcode, district_id=False):
        pass

    def send_create_email(self):
        pass

    def send_closed_email(self):
        pass

    def send_paid_email(self):
        pass

    def send_confirmed_email(self):
        pass


class OrderGoods(models.Model):
    _name = 'wechat_mall.order.goods'
    _description = u'订单商品'

    order_id = fields.Many2one('wechat_mall.order', string='订单', required=True, ondelete='cascade')

    # 冗余记录商品，防止商品删除后订单数据不完整
    goods_id = fields.Integer('商品id')
    name = fields.Char('商品名称', required=True)
    display_pic = fields.Html('图片', compute='_compute_display_pic')
    pic = fields.Many2one('ir.attachment', string='图片')
    property_str = fields.Char('商品规格')
    price = fields.Float('单价')
    amount = fields.Integer('商品数量')
    total = fields.Float('总价')

    @api.depends('pic')
    def _compute_display_pic(self):
        for each_record in self:
            if each_record.pic:
                each_record.display_pic = """
                <img src="{pic}" style="max-width:100px;">
                """.format(pic=each_record.pic[0].static_link())
            else:
                each_record.display_pic = False
