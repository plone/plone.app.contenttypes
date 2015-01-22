# -*- coding: utf-8 -*-
import pytz


def datetime_fixer(dt, zone):
    timezone = pytz.timezone(zone)
    if dt.tzinfo is None:
        return timezone.localize(dt)
    else:
        return timezone.normalize(dt)
