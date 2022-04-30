from Acquisition import aq_base
from logging import getLogger
from plone.app.contenttypes.behaviors.richtext import IRichText
from plone.app.contenttypes.interfaces import ICollection
from plone.app.contenttypes.interfaces import IDocument
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IFolder
from plone.app.contenttypes.interfaces import IImage
from plone.app.contenttypes.interfaces import ILink
from plone.app.contenttypes.interfaces import INewsItem
from plone.app.contenttypes.utils import replace_link_variables_by_paths
from plone.app.textfield.value import IRichTextValue
from plone.base.utils import human_readable_size
from plone.base.utils import safe_text
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer.decorator import indexer
from plone.rfc822.interfaces import IPrimaryFieldInfo
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.libtransforms.utils import MissingBinary
from ZODB.POSException import ConflictError


logger = getLogger(__name__)

FALLBACK_CONTENTTYPE = "application/octet-stream"


def _unicode_save_string_concat(*args):
    """
    concats args with spaces between and returns utf-8 string, it does not
    matter if input was text or bytes
    """
    result = ""
    for value in args:
        if isinstance(value, bytes):
            value = safe_text(value)
        result = " ".join((result, value))
    return result


def SearchableText(obj):
    text = ""
    richtext = IRichText(obj, None)
    if richtext:
        textvalue = richtext.text
        if IRichTextValue.providedBy(textvalue):
            transforms = getToolByName(obj, "portal_transforms")
            # Before you think about switching raw/output
            # or mimeType/outputMimeType, first read
            # https://github.com/plone/Products.CMFPlone/issues/2066
            raw = safe_text(textvalue.raw)
            text = (
                transforms.convertTo(
                    "text/plain",
                    raw,
                    mimetype=textvalue.mimeType,
                )
                .getData()
                .strip()
            )

    subject = " ".join([safe_text(s) for s in obj.Subject()])

    return " ".join(
        (
            safe_text(obj.id),
            safe_text(obj.title) or "",
            safe_text(obj.description) or "",
            safe_text(text),
            safe_text(subject),
        )
    )


@indexer(INewsItem)
def SearchableText_news(obj):
    return _unicode_save_string_concat(SearchableText(obj))


@indexer(IDocument)
def SearchableText_document(obj):
    return _unicode_save_string_concat(SearchableText(obj))


@indexer(ICollection)
def SearchableText_collection(obj):
    return _unicode_save_string_concat(SearchableText(obj))


@indexer(IFile)
def SearchableText_file(obj):
    try:
        primary_field = IPrimaryFieldInfo(obj)
    except TypeError:
        logger.warn(
            "Lookup of PrimaryField failed for {} "
            "If renaming or importing please reindex!".format(obj.absolute_url())
        )
        return
    if primary_field.value is None:
        return SearchableText(obj)
    mimetype = primary_field.value.contentType
    transforms = getToolByName(obj, "portal_transforms")
    if transforms._findPath(mimetype, "text/plain") is None:
        # check if there is a valid transform available first
        return SearchableText(obj)
    value = primary_field.value.data
    filename = primary_field.value.filename
    try:
        transformed_value = transforms.convertTo(
            "text/plain", value, mimetype=mimetype, filename=filename
        )
        if not transformed_value:
            return SearchableText(obj)
        return _unicode_save_string_concat(
            SearchableText(obj), transformed_value.getData()
        )
    except MissingBinary:
        return SearchableText(obj)
    except (ConflictError, KeyboardInterrupt):
        raise
    except Exception as msg:
        logger.exception(
            'exception while trying to convert blob contents to "text/plain" '
            "for {}. Error: {}".format(obj, str(msg)),
        )
        return SearchableText(obj)


@indexer(ILink)
def SearchableText_link(obj):
    if obj.remoteUrl:
        return _unicode_save_string_concat(SearchableText(obj), obj.remoteUrl)
    else:
        SearchableText(obj)


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
        logger.warn(
            "Lookup of PrimaryField failed for {} If renaming or importing "
            "please reindex!".format(obj.absolute_url())
        )
        return
    return human_readable_size(primary_field_info.value.size)


@indexer(IFile)
def getObjSize_file(obj):
    try:
        primary_field_info = IPrimaryFieldInfo(obj)
    except TypeError:
        logger.warn(
            "Lookup of PrimaryField failed for {} If renaming or importing "
            "please reindex!".format(obj.absolute_url())
        )
        return
    return human_readable_size(primary_field_info.value.size)


@indexer(IDexterityContent)
def mime_type(obj):
    return aq_base(obj).content_type()


@indexer(IDexterityContent)
def getIcon(obj):
    """
    geticon redefined in Plone > 5.0
    see https://github.com/plone/Products.CMFPlone/issues/1226

    reuse of metadata field,
    now used for showing thumbs in content listings etc.
    when obj is an image or has a lead image
    or has an image field with name 'image': true else false
    """
    if obj.aq_base.image:
        return True
    return False
