# -*- coding: utf-8 -*-

from odoo import models, fields

from .. import defs


class Logistics(models.Model):
    _name = 'wechat_mall.logistics'
    _description = u'物流'

    name = fields.Char('名称')
    free = fields.Boolean('是否包邮')
    valuation_type = fields.Selection(defs.LogisticsValuationType.attrs.items(), string='计价方式')

    transportation_ids = fields.One2many('wechat_mall.transportation', 'logistics_id', string='运送费用')

