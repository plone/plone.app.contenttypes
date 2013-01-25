# -*- coding: utf-8 -*-
from DateTime import DateTime

from plone.indexer.decorator import indexer

from plone.app.contenttypes.interfaces import IEvent, IDocument, INewsItem


@indexer(IEvent)
def start_date(obj):
    return DateTime(IEvent(obj).start_date)


@indexer(IEvent)
def end_date(obj):
    return DateTime(IEvent(obj).end_date)

@indexer(INewsItem)
def SearchableText_news(obj):
    return "%s %s %s" % (obj.title, obj.description, getattr(obj.text, 'output', ''))

@indexer(IDocument)
def SearchableText_document(obj):
    return "%s %s %s" % (obj.title, obj.description, getattr(obj.text, 'output', ''))
