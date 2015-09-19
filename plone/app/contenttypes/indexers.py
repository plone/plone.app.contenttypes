# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from ZODB.POSException import ConflictError
from logging import getLogger
from plone.app.contenttypes.interfaces import IDocument
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IFolder
from plone.app.contenttypes.interfaces import IImage
from plone.app.contenttypes.interfaces import ILink
from plone.app.contenttypes.interfaces import INewsItem
from plone.app.contenttypes.utils import replace_link_variables_by_paths
from plone.indexer.decorator import indexer
from plone.rfc822.interfaces import IPrimaryFieldInfo

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
        if value:
            result = ' '.join((result, value))
    return result


def SearchableText(obj, text=False):
    return u" ".join((
        safe_unicode(obj.id),
        safe_unicode(obj.title) or u"",
        safe_unicode(obj.description) or u"",
    ))


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
    try:
        primary_field = IPrimaryFieldInfo(obj)
    except TypeError:
        logger.warn(u'Lookup of PrimaryField failed for %s '
                    u'If renaming or importing please reindex!' %
                    obj.absolute_url())
        return
    if primary_field.value is None:
        return SearchableText(obj)
    mimetype = primary_field.value.contentType
    transforms = getToolByName(obj, 'portal_transforms')
    if transforms._findPath(mimetype, 'text/plain') is None:
        # check if there is a valid transform available first
        return SearchableText(obj)
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
    except Exception, msg:
        logger.exception('exception while trying to convert '
                         'blob contents to "text/plain" for %r. Error: %s' %
                         (obj, str(msg)))
        return SearchableText(obj)


@indexer(ILink)
def SearchableText_link(obj):
    return _unicode_save_string_concat(SearchableText(obj), obj.remoteUrl)


@indexer(IFolder)
def SearchableText_folder(obj):
    return SearchableText(obj)


@indexer(ILink)
def getRemoteUrl(obj):
    return replace_link_variables_by_paths(obj, obj.remoteUrl)


@indexer(IImage)
def getObjSize_image(obj):
    try:
        primary_field_info = IPrimaryFieldInfo(obj)
    except TypeError:
        logger.warn(u'Lookup of PrimaryField failed for %s '
                    u'If renaming or importing please reindex!' %
                    obj.absolute_url())
        return
    return obj.getObjSize(None, primary_field_info.value.size)


@indexer(IFile)
def getObjSize_file(obj):
    try:
        primary_field_info = IPrimaryFieldInfo(obj)
    except TypeError:
        logger.warn(u'Lookup of PrimaryField failed for %s '
                    u'If renaming or importing please reindex!' %
                    obj.absolute_url())
        return
    return obj.getObjSize(None, primary_field_info.value.size)


@indexer(IFile)
def getIcon_file(obj):
    """icon of the given mimetype,

    parts of this this code are borrowed from atct.
    """
    mtr = getToolByName(obj, 'mimetypes_registry', None)
    if mtr is None:
        return None

    try:
        primary_field_info = IPrimaryFieldInfo(obj, None)
    except TypeError:
        logger.warn(u'Lookup of PrimaryField failed for %s '
                    u'If renaming or importing please reindex!' %
                    obj.absolute_url())
        return
    if not primary_field_info.value:
        # There is no file so we should show a generic icon
        # TODO : find a better icon for generic
        return 'png.png'
        # return None

    contenttype = None
    if hasattr(primary_field_info.value, "contentType"):
        contenttype = primary_field_info.value.contentType
    if not contenttype:
        contenttype = FALLBACK_CONTENTTYPE

    mimetypeitem = None
    try:
        mimetypeitem = mtr.lookup(contenttype)
    except Exception, msg:
        logger.warn('mimetype lookup failed for %s. Error: %s' %
                    (obj.absolute_url(), str(msg)))

    if not mimetypeitem:
        mimetypeitem = mtr.lookup(FALLBACK_CONTENTTYPE)

    return mimetypeitem[0].icon_path


@indexer(IImage)
def getIcon_image(obj):
    return getIcon_file(obj)
