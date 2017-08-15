# -*- coding: utf-8 -*-

from odoo import models, fields


class City(models.Model):
    _name = 'wechat_mall.city'
    _description = u'市'

    pid = fields.Many2one('wechat_mall.province', string='省')
    name = fields.Char('名称')
    child_ids = fields.One2many('wechat_mall.district', 'pid', string='区')

