# -*- coding: utf-8 -*-
{
    'name': "wechat_mall",
    'application': True,

    'summary': """
        微信小程序商城管理后台""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Gzp",
    'website': "http://www.elfgzp.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

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
        'views/wechat_mall_transportation_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
