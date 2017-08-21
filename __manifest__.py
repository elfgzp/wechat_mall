# -*- coding: utf-8 -*-
{
    'name': "wechat_mall",
    'application': True,

    'summary': u"""
        微信小程序商城管理后台""",

    'description': u"""
        微信小程序商城管理后台
    """,

    'author': "Gzp",
    'website': "http://wechat.elfgzp.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/wechat_mall_security.xml',
        'security/ir.model.access.csv',
        'views/ir_attachment_view.xml',
        'views/parent_menus.xml',
        'views/wechat_mall_banner_views.xml',
        'views/wechat_mall_category_views.xml',
        'views/wechat_mall_city_views.xml',
        'views/wechat_mall_config_settings_views.xml',
        'views/wechat_mall_district_views.xml',
        'views/wechat_mall_goods_views.xml',
        'views/wechat_mall_logistics_views.xml',
        'views/wechat_mall_province_views.xml',
        'views/wechat_mall_subshop_views.xml',
        'views/wechat_mall_user_views.xml',
        'views/wechat_mall_address_views.xml',
        'views/wechat_mall_order_views.xml',
        'views/wechat_mall_shipper_views.xml',
        'views/wechat_mall_modify_price_wizard_views.xml',
        'views/wechat_mall_deliver_wizard_views.xml',
        'views/webclient_templates.xml',
        'data/order_num_sequence.xml',
        'data/payment_num_sequence.xml',
        'data/mail_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
