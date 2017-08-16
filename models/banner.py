# -*- coding: utf-8 -*-

from odoo import models, fields, api

from .. import defs


class Banner(models.Model):
    _name = 'wechat_mall.banner'
    _description = u'横幅'
    _rec_name = 'title'
    _order = 'sort'

    type_mark = fields.Integer(string='类型标记(用于扩展)', default=0)
    business_id = fields.Many2one('wechat_mall.goods', string='链接商品(可选)')
    title = fields.Char(string='名称', required=True)
    display_pic = fields.Html('图片', compute='_compute_display_pic')
    pic = fields.Many2one('ir.attachment', string='图片')
    link_url = fields.Char(string='链接地址')
    sort = fields.Integer(string='排序')
    status = fields.Boolean('显示', default=True, required=True)
    remark = fields.Text(string='备注')

    @api.depends('pic')
    def _compute_display_pic(self):
        for each_record in self:
            if each_record.pic:
                each_record.display_pic = """
                    <img src="{pic}" style="max-width:100px;">
                    """.format(pic=each_record.pic.static_link())
            else:
                each_record.display_pic = False
