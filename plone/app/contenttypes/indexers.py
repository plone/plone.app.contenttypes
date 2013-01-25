# -*- coding: utf-8 -*-
from DateTime import DateTime

from plone.indexer.decorator import indexer

from plone.app.contenttypes.interfaces import IEvent, IDocument


@indexer(IEvent)
def start_date(obj):
    return DateTime(IEvent(obj).start_date)


@indexer(IEvent)
def end_date(obj):
    return DateTime(IEvent(obj).end_date)

@indexer(IDocument)
def SearchableText(obj):
    return "%s %s %s" % (obj.Title(), obj.Description(), obj.text.output)
