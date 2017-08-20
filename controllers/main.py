# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

from odoo.addons.web.controllers.main import Home

import logging

_logger = logging.getLogger(__name__)


class WechatMallHome(Home):
    @http.route('/', type='http', auth="none")
    def index(self, s_action=None, db=None, **kw):
        return http.local_redirect('/web#menu_id={menu_id}&action={action_id}'.format(
            menu_id=request.env.ref('wechat_mall.wechat_mall_config_settings_menuitem_73').id,
            action_id=request.env.ref('wechat_mall.wechat_mall_config_settings_action_85').id,
        ), query=request.params, keep_hash=True)
