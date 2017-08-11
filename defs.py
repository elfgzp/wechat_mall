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


class LogisticsValuationType(Const):
    by_piece = ('by_piece', u'按件')


class TransportType(Const):
    express = ('express', u'快递')
    ems = ('ems', u'EMS')
    post = ('post', u'平邮')
