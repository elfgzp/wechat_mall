# -*- coding: utf-8 -*-

from odoo import models, fields


class Province(models.Model):
    _name = 'wechat_mall.province'
    _description = u'省'

    name = fields.Char('名称')
    child_ids = fields.One2many('wechat_mall.city', 'pid', string='市')
