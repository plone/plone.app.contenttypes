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

FALLBACK_CONTENTTYPE = 'application/octet-stream'


def _unicode_save_string_concat(*args):
    """
    concats args with spaces between and returns utf-8 string, it does not
    matter if input was unicode or str
    """
    result = ''
    for value in args:
        if isinstance(value, unicode):
            value = value.encode('utf-8', 'replace')
        result = ' '.join((result, value))
    return result


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
    return _unicode_save_string_concat(SearchableText(obj), obj.text.output)


@indexer(IDocument)
def SearchableText_document(obj):
    if obj.text is None or obj.text.output is None:
        return SearchableText(obj)
    return _unicode_save_string_concat(SearchableText(obj), obj.text.output)


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
        return _unicode_save_string_concat(SearchableText(obj),
                                           transformed_value.getData())
    except (ConflictError, KeyboardInterrupt):
        raise
    except:
        logger.exception('exception while trying to convert '
                         'blob contents to "text/plain" for %r', obj)
        return SearchableText(obj)


@indexer(ILink)
def SearchableText_link(obj):
    return _unicode_save_string_concat(SearchableText(obj), obj.remoteUrl)


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


@indexer(IFile)
def getIcon_file(obj):
    """icon of the given mimetype,

    parts of this this code are borrowed form atct.
    """
    mtr = getToolByName(obj, 'mimetypes_registry', None)
    if mtr is None:
        return None

    primary_field_info = IPrimaryFieldInfo(obj)
    if not primary_field_info.value:
        return None

    contenttype = primary_field_info.value.contentType
    if not contenttype:
        contenttype = FALLBACK_CONTENTTYPE

    mimetypeitem = None
    try:
        mimetypeitem = mtr.lookup(contenttype)
    except Exception, msg:
        logger.warn('mimetype lookup falied for %s. Error: %s' %
                    (obj.absolute_url(), str(msg)))

    if not mimetypeitem:
        mimetypeitem = mtr.lookup(FALLBACK_CONTENTTYPE)

    return mimetypeitem[0].icon_path


@indexer(IImage)
def getIcon_image(obj):
    return getIcon_file(obj)
