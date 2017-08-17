# -*- coding: utf-8 -*-


from odoo import models, fields, api


class ConfirmWizard(models.TransientModel):
    _name = 'wechat_mall.confirm'
    _description = u'确认弹窗'

    info = fields.Text("通知信息")
    info_char = fields.Char("通知信息-Char")
    info_html = fields.Html("通知信息-HTML")
