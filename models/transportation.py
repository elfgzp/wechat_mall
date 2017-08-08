# -*- coding: utf-8 -*-

from odoo import models, fields

from .. import defs


class Transportation(models.Model):
    _name = 'wechat_mall.transportation'
    _description = u'运输费'

    user_id = fields.Many2one('res.users', string='所属用户')
    logistics_id = fields.Many2one('wechat_mall.logistics', string='物流')
    transport_type = fields.Selection(defs.TransportType.attrs.items(), string='运输方式', required=True)
    province_id = fields.Many2one('wechat_mall.province', string='省', required=True)
    city_id = fields.Many2one('wechat_mall.city', string='市', required=True)
    district_id = fields.Many2one('wechat_mall.district', string='区', required=True)
    less_amount = fields.Integer('数量', required=True)
    less_price = fields.Float('数量内价格', required=True)
    beyond_amount = fields.Integer('超过数量', required=True)
    beyond_price = fields.Float('递增价格', required=True)