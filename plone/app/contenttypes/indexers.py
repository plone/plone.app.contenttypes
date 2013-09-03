# -*- coding: utf-8 -*-
from DateTime import DateTime
from logging import getLogger

from Products.CMFCore.utils import getToolByName
from ZODB.POSException import ConflictError

from plone.indexer.decorator import indexer
from plone.rfc822.interfaces import IPrimaryFieldInfo

from plone.app.contenttypes.interfaces import (
    IEvent, IDocument, INewsItem, ILink, IImage, IFile, IFolder
)

logger = getLogger(__name__)


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
    if obj.text is None or obj.text.output is None:
        return SearchableText(obj)
    return ' '.join((SearchableText(obj), obj.text.output))


@indexer(IDocument)
def SearchableText_document(obj):
    if obj.text is None or obj.text.output is None:
        return SearchableText(obj)
    return ' '.join((SearchableText(obj), obj.text.output))


@indexer(IFile)
def SearchableText_file(obj):
    primary_field = IPrimaryFieldInfo(obj)
    if primary_field.value is None:
        return SearchableText(obj)
    mimetype = primary_field.value.contentType
    transforms = getToolByName(obj, 'portal_transforms')
    value = str(primary_field.value.data)
    filename = primary_field.value.filename
    try:
        transformed_value = transforms.convertTo('text/plain', value,
                                                 mimetype=mimetype,
                                                 filename=filename)
        if not transformed_value:
            return SearchableText(obj)
        transformed_value = unicode(transformed_value).encode('utf-8',
                                                              'replace')
        return ' '.join((SearchableText(obj), transformed_value))
    except (ConflictError, KeyboardInterrupt):
        raise
    except:
        logger.exception('exception while trying to convert '
                         'blob contents to "text/plain" for %r', obj)
        return SearchableText(obj)


@indexer(ILink)
def SearchableText_link(obj):
    return ' '.join((SearchableText(obj), obj.remoteUrl))


@indexer(IFolder)
def SearchableText_folder(obj):
    return SearchableText(obj)


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
