# -*- coding: utf-8 -*-

from .utils import Const


class LogisticsValuationType(Const):
    by_piece = ('by_piece', u'按件')


class TransportType(Const):
    express = ('express', u'快递')
    ems = ('ems', u'EMS')
    post = ('post', u'平邮')
