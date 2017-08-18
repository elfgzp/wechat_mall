# -*- coding: utf-8 -*-

from odoo import models, fields, api
from kdniao.client import KdNiaoClient

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
    full_address = fields.Char('联系人地址', compute='_compute_full_address')
    postcode = fields.Char('邮政编码', requried=True)

    shipper_id = fields.Many2one('wechat_mall.shipper', string='快递承运商', track_visibility='onchange')
    tracking_number = fields.Char('运单号', track_visibility='onchange')
    display_traces = fields.Text('物流信息', compute='_compute_display_traces')
    traces = fields.Text('物流信息', compute='_compute_traces')

    @api.model
    def create(self, vals):
        vals['order_num'] = self.env['ir.sequence'].next_by_code('wechat_mall.order_num')
        return super(Order, self).create(vals)

    @api.one
    @api.depends('province_id', 'city_id', 'district_id', 'address')
    def _compute_full_address(self):
        self.full_address = '{province_name} {city_name} {district_name} {address}'.format(
            province_name=self.province_id.name,
            city_name=self.city_id.name,
            district_name=self.district_id.name or '',
            address=self.address
        )

    @api.one
    @api.depends('shipper_id', 'tracking_number')
    def _compute_display_traces(self):
        config = self.env['wechat_mall.config.settings']
        kdniao_app_id = config.get_config('kdniao_app_id')
        kdniao_app_key = config.get_config('kdniao_app_key')
        if not kdniao_app_id or not kdniao_app_key:
            self.display_traces = '无法查询物流信息，请检查基本设置中的"快递鸟物流查询设置"是否设置完整。'
        elif not self.shipper_id or not self.tracking_number:
            self.display_traces = '无法查询物流信息，请检查订单中的"快递承运商"和"运单号"是否设置完整。'
        else:
            traces = KdNiaoClient(kdniao_app_id, kdniao_app_key).track(self.tracking_number, self.shipper_id.code)
            r = traces or {}

            r_data = r.get('data', {})
            trace_list = r_data.get('Traces', [])

            if trace_list:
                msg_temp = '%s - %s'
                msg_list = [msg_temp % (i['AcceptTime'], i['AcceptStation']) for i in trace_list]
                self.display_traces = '\n'.join(msg_list)
            else:
                self.display_traces = r_data['Reason']


    @api.one
    @api.depends('shipper_id', 'tracking_number')
    def _compute_traces(self):
        config = self.env['wechat_mall.config.settings']
        kdniao_app_id = config.get_config('kdniao_app_id')
        kdniao_app_key = config.get_config('kdniao_app_key')
        if not kdniao_app_id or not kdniao_app_key:
            self.traces = '{}'
        elif not self.shipper_id or not self.tracking_number:
            self.traces = '{}'
        else:
            traces = KdNiaoClient(kdniao_app_id, kdniao_app_key).track(self.tracking_number, self.shipper_id.code)
            self.traces = traces

    # todo 订单邮件提醒
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
