# -*- coding: utf-8 -*-
from DateTime import DateTime

from plone.indexer.decorator import indexer
from plone.rfc822.interfaces import IPrimaryFieldInfo

from plone.app.contenttypes.interfaces import (
    IEvent, IDocument, INewsItem, ILink, IImage, IFile
)


@indexer(IEvent)
def start_date(obj):
    return DateTime(IEvent(obj).start_date)


@indexer(IEvent)
def end_date(obj):
    return DateTime(IEvent(obj).end_date)


def SearchableText(obj, text=False):
    return ' '.join((obj.id, obj.title, obj.description, ))


@indexer(INewsItem)
def SearchableText_news(obj):
    return ' '.join((SearchableText(obj), getattr(obj.text, 'output', '')))


@indexer(IDocument)
def SearchableText_document(obj):
    return ' '.join((SearchableText(obj), getattr(obj.text, 'output', '')))


@indexer(ILink)
def SearchableText_link(obj):
    return ' '.join((SearchableText(obj), obj.remoteUrl))


@indexer(ILink)
def getRemoteUrl(obj):
    return obj.remoteUrl


@indexer(IImage)
def getObjSize_image(obj):
    primary_field_info = IPrimaryFieldInfo(obj)
    return obj.getObjSize(None, primary_field_info.value.size)


@indexer(IFile)
def getObjSize_file(obj):
    primary_field_info = IPrimaryFieldInfo(obj)
    return obj.getObjSize(None, primary_field_info.value.size)
