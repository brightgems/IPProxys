﻿# coding:utf-8

def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return u"刚刚"
        if second_diff < 60:
            return str(second_diff) + u" 秒前"
        if second_diff < 120:
            return u"1分钟前"
        if second_diff < 3600:
            return str(second_diff / 60) + u" 秒前"
        if second_diff < 7200:
            return u"1小时前"
        if second_diff < 86400:
            return str(second_diff / 3600) + u" 小时前"
    if day_diff == 1:
        return u"昨日"
    if day_diff < 7:
        return str(day_diff) + u" 天前"
    if day_diff < 31:
        return str(day_diff / 7) + u" 周前"
    if day_diff < 365:
        return str(day_diff / 30) + u" 月前"
    return str(day_diff / 365) + u" 年前"
