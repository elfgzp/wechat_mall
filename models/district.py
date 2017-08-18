# -*- coding: utf-8 -*-

from odoo import models, fields, api


class District(models.Model):
    _name = 'wechat_mall.district'
    _description = u'区'

    pid = fields.Many2one('wechat_mall.city', string='市')
    name = fields.Char('名称')

    @api.model_cr
    def _register_hook(self):
        """ stuff to do right after the registry is built """
        from ..data import province_city_district_data
        self.env.cr.execute(province_city_district_data)
