# -*- coding: utf-8 -*-
from plone.app.textfield.value import RichTextValue
from plone.event.utils import default_timezone
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from Products.CMFPlone.utils import safe_hasattr
from Products.CMFPlone.utils import safe_unicode

import logging
import pytz


logger = logging.getLogger(__name__)


def migrate_simplefield(src_obj, dst_obj, src_fieldname, dst_fieldname):
    """Migrate a generic simple field.

    Copies the value of a Archetypes-object to a attribute of the same name
    to the target-object. The only transform is a safe_unicode of the value.
    """
    field = src_obj.getField(src_fieldname)
    if field:
        at_value = field.get(src_obj)
    else:
        at_value = getattr(src_obj, src_fieldname, None)
        if at_value and hasattr(at_value, '__call__'):
            at_value = at_value()
    if isinstance(at_value, tuple):
        at_value = tuple(safe_unicode(i) for i in at_value)
    if isinstance(at_value, list):
        at_value = [safe_unicode(i) for i in at_value]
    if at_value:
        setattr(dst_obj, dst_fieldname, safe_unicode(at_value))


def migrate_richtextfield(src_obj, dst_obj, src_fieldname, dst_fieldname):
    """
    migrate a rich text field.
    This field needs some extra stuffs like keep the same mimetype.
    """
    field = src_obj.getField(src_fieldname)
    raw_text = ''
    if field:
        mime_type = field.getContentType(src_obj)
        raw_text = safe_unicode(field.getRaw(src_obj))
    else:
        at_value = getattr(src_obj, src_fieldname, None)
        if at_value:
            mime_type = at_value.mimetype
            raw_text = safe_unicode(at_value.raw)

    if raw_text.strip() == '':
        return
    richtext = RichTextValue(raw=raw_text, mimeType=mime_type,
                             outputMimeType='text/x-html-safe')
    setattr(dst_obj, dst_fieldname, richtext)


def migrate_imagefield(src_obj, dst_obj, src_fieldname, dst_fieldname):
    """
    migrate an image field.
    This field needs to be migrated with an NamedBlobImage instance.
    """
    # get old image data and filename
    field = src_obj.getField(src_fieldname)
    accessor = field.getAccessor(src_obj)
    old_image = accessor()
    if old_image == '':
        return
    filename = safe_unicode(old_image.filename)
    old_image_data = old_image.data
    if safe_hasattr(old_image_data, 'data'):
        old_image_data = old_image_data.data

    # create the new image field
    namedblobimage = NamedBlobImage(data=old_image_data,
                                    filename=filename)

    # set new field on destination object
    setattr(dst_obj, dst_fieldname, namedblobimage)

    # handle a possible image caption field
    # postulate is the old caption field name is ending by 'Caption'
    # and the new field name is ending by '_caption'
    # is this postulate correct ?
    # should this field not be handle by itself because it will appear in the
    # old field list ?
    caption_field = src_obj.getField('{0}Caption'.format(src_fieldname), None)
    if caption_field:
        setattr(dst_obj,
                ('{0}_caption'.format(dst_fieldname)),
                safe_unicode(caption_field.get(src_obj)))

    logger.info(u'Migrating image {0}'.format(filename))


def migrate_blobimagefield(src_obj, dst_obj, src_fieldname, dst_fieldname):
    """
    migrate an image field.
    Actually this field needs only to copy the existing NamedBlobImage instance
    to the new dst_obj, but we do some more in detail and create new fields.
    """
    old_image = getattr(src_obj, src_fieldname)
    if old_image == '':
        return
    filename = safe_unicode(old_image.filename)
    old_image_data = old_image.data
    if safe_hasattr(old_image_data, 'data'):
        old_image_data = old_image_data.data
    namedblobimage = NamedBlobImage(data=old_image_data,
                                    filename=filename)

    # set new field on destination object
    setattr(dst_obj, dst_fieldname, namedblobimage)

    # handle a possible image caption field
    field = '{0}_caption'.format(src_fieldname)
    old_image_caption = getattr(src_obj, field, None)
    if old_image_caption:
        setattr(dst_obj,
                ('{0}_caption'.format(dst_fieldname)),
                safe_unicode(old_image_caption))

    logger.info(u'Migrating image {0}'.format(filename))


def migrate_filefield(src_obj, dst_obj, src_fieldname, dst_fieldname):
    """
    migrate a file field.
    This field needs to be migrated with an NamedBlobFile instance.
    """
    old_file = src_obj.getField(src_fieldname).get(src_obj)
    if old_file == '':
        return
    filename = safe_unicode(old_file.filename)
    old_file_data = old_file.data
    if safe_hasattr(old_file_data, 'data'):
        old_file_data = old_file_data.data
    namedblobfile = NamedBlobFile(
        contentType=old_file.content_type,
        data=old_file_data,
        filename=filename)
    setattr(dst_obj, dst_fieldname, namedblobfile)
    logger.info(u'Migrating file {0}'.format(filename))


def migrate_datetimefield(src_obj, dst_obj, src_fieldname, dst_fieldname):
    """Migrate a datefield."""
    old_value = src_obj.getField(src_fieldname).get(src_obj)
    if old_value == '':
        return
    if src_obj.getField('timezone', None) is not None:
        old_timezone = src_obj.getField('timezone').get(src_obj)
    else:
        old_timezone = default_timezone(fallback='UTC')
    new_value = datetime_fixer(old_value.asdatetime(), old_timezone)
    setattr(dst_obj, dst_fieldname, new_value)


def datetime_fixer(dt, zone):
    timezone = pytz.timezone(zone)
    if dt.tzinfo is None:
        return timezone.localize(dt)
    else:
        return timezone.normalize(dt)


# This mapping is needed to get the right migration method
# we use the full field type path as it is retrieved from the target-field
# (field.getType()), to avoid conflict.
# TODO In the __future__ we should have a more dynamic way to configure this
# mapping
FIELDS_MAPPING = {'RichText': migrate_richtextfield,
                  'NamedBlobFile': migrate_filefield,
                  'NamedBlobImage': migrate_imagefield,
                  'Datetime': migrate_datetimefield,
                  'Date': migrate_datetimefield}
