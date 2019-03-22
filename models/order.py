# -*- coding: utf-8 -*-

import json

from odoo import models, fields, api
from kdniao.client import KdNiaoClient

from .. import defs


class Order(models.Model):
    _name = 'wechat_mall.order'
    _description = u'订单'
    _inherit = ['mail.thread']
    _rec_name = 'order_num'
    _order = 'create_date desc'

    wechat_user_id = fields.Many2one('wechat_mall.user', string='微信用户')
    order_num = fields.Char('订单号', index=True)
    goods_ids = fields.Many2many('wechat_mall.goods', string='商品', help='真实商品数据，保留便于查询。')
    order_goods_ids = fields.One2many('wechat_mall.order.goods', 'order_id',
                                      string='订单商品', help='商品参数数据冗余，防止商品修改或删除。')
    number_goods = fields.Integer('商品数量')
    goods_price = fields.Float('商品总金额', requried=True, default=0)
    logistics_price = fields.Float('物流费用', requried=True, default=0)
    total = fields.Float('实际支付', requried=True, default=0, track_visibility='onchange')
    status = fields.Selection(list(defs.OrderStatus.attrs.items()), default=defs.OrderStatus.unpaid,
                              required=True, string='状态', track_visibility='onchange')

    remark = fields.Char('备注')
    linkman = fields.Char('联系人')
    phone = fields.Char('手机号码')
    province_id = fields.Many2one('wechat_mall.province', string='省', required=True)
    city_id = fields.Many2one('wechat_mall.city', string='市', required=True)
    district_id = fields.Many2one('wechat_mall.district', string='区')
    address = fields.Char('详细地址')
    full_address = fields.Char('联系人地址', compute='_compute_full_address', store=True)
    postcode = fields.Char('邮政编码', requried=True)

    shipper_id = fields.Many2one('wechat_mall.shipper', string='快递承运商', track_visibility='onchange')
    tracking_number = fields.Char('运单号', track_visibility='onchange')
    display_traces = fields.Html('物流信息', compute='_compute_display_traces')
    traces = fields.Text('物流信息', compute='_compute_traces')

    payment_ids = fields.One2many('wechat_mall.payment', 'order_id', '支付记录')

    _sql_constraints = [(
        'wechat_mall_order_order_num_unique',
        'UNIQUE (order_num)',
        'wechat order order_num is existed！'
    )]

    @api.model
    def create(self, vals):
        vals['order_num'] = self.env['ir.sequence'].next_by_code('wechat_mall.order_num')
        return super(Order, self).create(vals)

    @api.one
    @api.depends('province_id', 'city_id', 'district_id', 'address')
    def _compute_full_address(self):
        self.full_address = u'{province_name} {city_name} {district_name} {address}'.format(
            province_name=self.province_id.name,
            city_name=self.city_id.name,
            district_name=self.district_id.name or '',
            address=self.address
        )

    @api.one
    @api.depends('shipper_id', 'tracking_number')
    def _compute_display_traces(self):
        config = self.env['wechat_mall.config.settings']
        kdniao_app_id = config.get_config('kdniao_app_id', uid=self.create_uid.id)
        kdniao_app_key = config.get_config('kdniao_app_key', uid=self.create_uid.id)
        if not kdniao_app_id or not kdniao_app_key:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            config_action_id = self.env.ref('wechat_mall.wechat_mall_config_settings_action_85').id
            config_menu_id = self.env.ref('wechat_mall.wechat_mall_config_settings_menuitem_73').id
            link = '{base_url}/web#menu_id={menu_id}&action={action_id}'.format(
                base_url=base_url,
                menu_id=config_menu_id,
                action_id=config_action_id,

            )
            self.display_traces = \
                '<p>无法查询物流信息，请检查<a href="{config_link}"><span>基本设置</span></a>中的"快递鸟物流查询设置"是否设置完整。</p>'.format(
                    config_link=link
                )
        elif not self.shipper_id or not self.tracking_number:
            self.display_traces = '<p>无法查询物流信息，请检查订单中的"快递承运商"和"运单号"是否设置完整。</p>'
        else:
            traces = KdNiaoClient(kdniao_app_id, kdniao_app_key).track(self.tracking_number, self.shipper_id.code)
            r = traces or {}

            r_data = r.get('data', {})
            trace_list = r_data.get('Traces', [])

            if trace_list:
                msg_temp = '<p>%s - %s</p>'
                msg_list = [msg_temp % (i['AcceptTime'], i['AcceptStation']) for i in trace_list]
                self.display_traces = '<br>'.join(msg_list)
            else:
                self.display_traces = '<p>%s</p>' % r_data['Reason']

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
            self.traces = json.dumps(traces)

    @api.multi
    def order_link(self):
        result = []
        for each_record in self:
            order_action_id = self.env.ref('wechat_mall.wechat_mall_order_action_134').id
            order_menu_id = self.env.ref('wechat_mall.wechat_mall_order_menuitem_118').id
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            link = '{base_url}/web#id={order_id}&view_type=form&model=wechat_mall.order&menu_id={menu_id}&action={action_id}'.format(
                base_url=base_url,
                order_id=self.id,
                menu_id=order_menu_id,
                action_id=order_action_id,

            )
            result.append((each_record.id, link))

        return result

    def paid(self):
        self.ensure_one()
        self.write({'status': 'pending'})

    def deliver(self):
        context = self._context.copy() or {}
        context['default_order_id'] = self.id
        context['default_status'] = 'unconfirmed'
        return {
            'name': u'发货信息设置',
            'type': 'ir.actions.act_window',
            'res_model': 'wechat_mall.deliver.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': context,
        }

    def confirm(self):
        self.ensure_one()
        self.write({'status': 'completed'})

    def cancel(self):
        self.ensure_one()
        self.write({'status': 'closed'})

    def modify_price(self):
        context = self._context.copy() or {}
        context['default_order_id'] = self.id
        return {
            'name': u'订单价格修改',
            'type': 'ir.actions.act_window',
            'res_model': 'wechat_mall.modify.price.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': context,
        }

    def modify_logistics_info(self):
        context = self._context.copy() or {}
        context['default_order_id'] = self.id
        context['default_status'] = self.status
        return {
            'name': u'发货信息修改',
            'type': 'ir.actions.act_window',
            'res_model': 'wechat_mall.deliver.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': context,
        }


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
                """.format(pic=each_record.pic.static_link())
            else:
                each_record.display_pic = False


class ModifyPriceWizard(models.TransientModel):
    _name = 'wechat_mall.modify.price.wizard'
    _description = u'修改价格'

    order_id = fields.Many2one('wechat_mall.order', string='订单', required=True)
    total = fields.Float('金额', required=True)

    @api.model
    def create(self, vals):
        order = self.env['wechat_mall.order'].browse(vals.pop('order_id'))
        order.write(vals)
        return super(ModifyPriceWizard, self).create(vals)

    @api.multi
    def apply(self):
        return {'type': 'ir.actions.client', 'tag': 'reload'}


class DeliverWizard(models.TransientModel):
    _name = 'wechat_mall.deliver.wizard'
    _description = u'发货'

    order_id = fields.Many2one('wechat_mall.order', string='订单')
    shipper_id = fields.Many2one('wechat_mall.shipper', string='快递承运商')
    tracking_number = fields.Char('运单号')
    status = fields.Char('状态', required=True)

    @api.model
    def create(self, vals):
        order = self.env['wechat_mall.order'].browse(vals.pop('order_id'))
        vals['tracking_number'] = vals.get('tracking_number').replace(' ', '') if vals.get(
            'tracking_number') is not False else ''
        order.write(vals)
        return super(DeliverWizard, self).create(vals)

    @api.multi
    def apply(self):
        return {'type': 'ir.actions.client', 'tag': 'reload'}
