# -*- coding: utf-8 -*-

from odoo import models, fields, api

from .. import defs


class Shipper(models.Model):
    _name = 'wechat_mall.shipper'
    _description = u'承运商'

    name = fields.Char('名称')
    code = fields.Char('编码')

    @api.model_cr
    def _register_hook(self):
        """ stuff to do right after the registry is built """
        from ..data import shipper_data
        self.env.cr.execute(shipper_data)

