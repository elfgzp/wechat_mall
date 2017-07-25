# -*- coding: utf-8 -*-
from odoo import http

# class WechatMall(http.Controller):
#     @http.route('/wechat_mall/wechat_mall/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wechat_mall/wechat_mall/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wechat_mall.listing', {
#             'root': '/wechat_mall/wechat_mall',
#             'objects': http.request.env['wechat_mall.wechat_mall'].search([]),
#         })

#     @http.route('/wechat_mall/wechat_mall/objects/<model("wechat_mall.wechat_mall"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wechat_mall.object', {
#             'object': obj
#         })