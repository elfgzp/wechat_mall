# -*- coding: utf-8 -*-

from odoo import models, fields, api

from .. import defs


class Address(models.Model):
    _name = 'wechat_mall.address'
    _description = u'用户收货地址'
    _rec_name = 'linkman'

    wechat_user_id = fields.Many2one('wechat_mall.user', string='微信用户', ondelete='cascade')

    linkman = fields.Char('联系人')
    phone = fields.Char('手机号码')
    province_id = fields.Many2one('wechat_mall.province', string='省', required=True)
    city_id = fields.Many2one('wechat_mall.city', string='市', required=True)
    district_id = fields.Many2one('wechat_mall.district', string='区')
    address = fields.Char('详细地址')
    postcode = fields.Char('邮政编码', requried=True)
    status = fields.Boolean('启用', default=True)
    status_str = fields.Char('状态', compute='_compute_status_str')
    is_default = fields.Boolean('是否为默认地址')

    city_domain_ids = fields.One2many('wechat_mall.city', compute='_compute_city_domain_ids')
    district_domain_ids = fields.One2many('wechat_mall.district', compute='_compute_district_domain_ids')

    @api.multi
    @api.depends('status')
    def _compute_status_str(self):
        for each_record in self:
            each_record.status_str = defs.AddressStatus.attrs[each_record.status]

    @api.onchange('province_id')
    def _onchange_province_id(self):
        self.city_domain_ids = self.province_id.child_ids if self.province_id else False
        self.city_id = False
        self.district_id = False
        return {
            'domain': {
                'city_id': [('id', 'in', self.city_domain_ids.ids if self.city_domain_ids else [0])]
            }
        }

    @api.onchange('city_id')
    def _onchange_city_id(self):
        self.district_domain_ids = self.city_id.child_ids if self.city_id else False
        self.district_id = False
        return {
            'domain': {
                'district_id': [('id', 'in', self.district_domain_ids.ids if self.district_domain_ids else [0])]
            }
        }

    @api.depends('province_id')
    def _compute_city_domain_ids(self):
        self.city_domain_ids = self.province_id.child_ids if self.province_id else False

    @api.depends('city_id')
    def _compute_district_domain_ids(self):
        self.district_domain_ids = self.city_id.child_ids if self.city_id else False
