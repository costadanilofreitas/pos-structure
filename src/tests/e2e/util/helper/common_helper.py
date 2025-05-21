# -*- coding: utf-8 -*-

import datetime

from dateutil import tz


def convert_from_localtime_to_utc(localtime):
    # type: (datetime) -> datetime
    from_zone = tz.tzlocal()
    to_zone = tz.tzutc()
    localtime = localtime.replace(tzinfo=from_zone)
    utc = localtime.astimezone(to_zone)
    return utc
