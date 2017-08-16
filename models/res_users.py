# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    sub_domain = fields.Char('子域名', help='用于小程序接口的子域名。', index=True)

    @api.model
    def create(self, vals):
        from uuid import uuid1
        vals['sub_domain'] = uuid1().get_hex()
        return super(ResUsers, self).create(vals)
