# -*- coding: utf-8 -*-

from .utils import Const


class BannerStatus(Const):
    visible = (True, u'显示')
    invisible = (False, u'不显示')


class GoodsRecommendStatus(Const):
    normal = (False, u'普通')
    recommend = (True, u'推荐')


class GoodsStatus(Const):
    put_away = (True, u'上架')
    sold_out = (False, u'下架')


class AddressStatus(Const):
    regular = (True, u'正常')
    irregular = (False, u'禁用')


class LogisticsValuationType(Const):
    by_piece = ('by_piece', u'按件')
    by_weight = ('by_weight', u'按重量')


class LogisticsValuationApiType(Const):
    by_piece = ('by_piece', 0)
    by_weight = ('by_weight', 1)


class TransportationUnit(Const):
    by_piece = ('by_piece', u'件')
    by_weight = ('by_weight', u'KG')


class TransportType(Const):
    express = ('express', u'快递')
    ems = ('ems', u'EMS')
    post = ('post', u'平邮')


class TransportApiType(Const):
    express = ('express', 0)
    ems = ('ems', 1)
    post = ('post', 2)


class WechatUserRegisterType(Const):
    app = ('app', u'小程序')


class WechatUserStatus(Const):
    default = ('default', u'默认')
