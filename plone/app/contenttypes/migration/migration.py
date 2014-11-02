# -*- coding: utf-8 -*-
'''
Migrating ATContentTypes to plone.app.contenttypes objects.

This module imports from Product.contentmigration on which we depend
only in the setuptools extra_requiers [migrate_atct]. Importing this
module will only work if Products.contentmigration is installed so make sure
you catch ImportErrors
'''
from persistent.list import PersistentList
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.app.contenttypes.migration import datetime_fixer
from plone.app.contenttypes.migration.dxmigration import DXEventMigrator
from plone.app.contenttypes.migration.dxmigration import DXOldEventMigrator
from plone.app.textfield.value import RichTextValue
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.interfaces import IDexterityContent
from plone.event.utils import default_timezone
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.ATContentTypes.interfaces.interfaces import IATContentType
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode, safe_hasattr
from Products.contentmigration.basemigrator.migrator import CMFFolderMigrator
from Products.contentmigration.basemigrator.migrator import CMFItemMigrator
from Products.contentmigration.basemigrator.walker import CatalogWalker
from Products.contentmigration.walker import CustomQueryWalker
import transaction
from z3c.relationfield import RelationValue
from zope.component import adapter
from zope.component import getAdapters
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import Interface
from zope.intid.interfaces import IIntIds
import logging

logger = logging.getLogger(__name__)


def migrate_simplefield(src_obj, dst_obj, src_fieldname, dst_fieldname):
    """
    migrate a generic simple field (like a string field or a date field)
    """
    field = src_obj.getField(src_fieldname)
    if field:
        at_value = field.get(src_obj)
    else:
        at_value = getattr(src_obj, src_fieldname, None)
        if at_value and hasattr(at_value, '__call__'):
            at_value = at_value()
    if at_value:
        setattr(dst_obj, dst_fieldname, at_value)


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
    old_image = src_obj.getField(src_fieldname).get(src_obj)
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
    caption_field = src_obj.getField('%sCaption' % src_fieldname, None)
    if caption_field:
        setattr(dst_obj,
                ('%s_caption' % dst_fieldname),
                safe_unicode(caption_field.get(src_obj)))

    logger.info("Migrating image %s" % filename)


def migrate_filefield(src_obj, dst_obj, src_fieldname, dst_fieldname):
    """
    migrate an image field.
    This field needs to be migrated with an NamedBlobFile instance.
    BBB to be tested
    """
    old_file = src_obj.getField(src_fieldname).get(src_obj)
    if old_file == '':
        return
    filename = safe_unicode(old_file.filename)
    old_file_data = old_file.data
    if safe_hasattr(old_file_data, 'data'):
        old_file_data = old_file_data.data
    namedblobfile = NamedBlobFile(data=old_file_data,
                                    filename=filename)
    setattr(dst_obj, dst_fieldname, namedblobfile)
    logger.info("Migrating file %s" % filename)


# this mapping is needed to use the right migration method
# we use the full field type path as it is retrieved from the field
# (field.getType()), to avoid conflict.
# TODO In the __future__ we should have a more dynamic way to configure this
# mapping
FIELDS_MAPPING = {'Products.Archetypes.Field.TextField': migrate_richtextfield,
                  'Products.Archetypes.Field.FileField': migrate_filefield,
                  'plone.app.blob.field.FileField': migrate_filefield,
                  'Products.Archetypes.Field.ImageField': migrate_imagefield}


def migrate(portal, migrator):
    """return a CatalogWalker instance in order
    to have its output after migration"""
    walker = CatalogWalker(portal, migrator)()
    return walker


def refs(obj):
    intids = getUtility(IIntIds)
    out = ''

    try:
        if not getattr(obj, 'relatedItems', None):
            obj.relatedItems = PersistentList()

        elif type(obj.relatedItems) != type(PersistentList()):
            obj.relatedItems = PersistentList(obj.relatedItems)

        for uuid in obj._relatedItems:
            to_obj = uuidToObject(uuid)
            to_id = intids.getId(to_obj)
            obj.relatedItems.append(RelationValue(to_id))
            out += str('Restore Relation from %s to %s \n' % (obj, to_obj))
        del obj._relatedItems

    except AttributeError:
        pass
    return out


def backrefs(portal, obj):
    intids = getUtility(IIntIds)
    uid_catalog = getToolByName(portal, 'uid_catalog')
    out = ''

    try:
        backrefobjs = [uuidToObject(uuid) for uuid in obj._backrefs]
        for backrefobj in backrefobjs:
            # Dexterity and
            if IDexterityContent.providedBy(backrefobj):
                relitems = getattr(backrefobj, 'relatedItems', None)
                if not relitems:
                    backrefobj.relatedItems = PersistentList()
                elif type(relitems) != type(PersistentList()):
                    backrefobj.relatedItems = PersistentList(
                        obj.relatedItems
                    )
                to_id = intids.getId(obj)
                backrefobj.relatedItems.append(RelationValue(to_id))

            # Archetypes
            elif IATContentType.providedBy(backrefobj):
                # reindex UID so we are able to set the reference
                path = '/'.join(obj.getPhysicalPath())
                uid_catalog.catalog_object(obj, path)
                backrefobj.setRelatedItems(obj)
            out += str(
                'Restore BackRelation from %s to %s \n' % (
                    backrefobj,
                    obj
                )
            )
        del obj._backrefs
    except AttributeError:
        pass
    return out


def order(obj):
    out = ''
    if not hasattr(obj, '_relatedItemsOrder'):
        # Nothing to do
        return out

    relatedItemsOrder = obj._relatedItemsOrder
    uid_position_map = dict([(y, x) for x, y in enumerate(relatedItemsOrder)])
    key = lambda rel: uid_position_map.get(rel.to_object.UID(), 0)
    obj.relatedItems = sorted(obj.relatedItems, key=key)
    out += str('%s ordered.' % obj)
    del obj._relatedItemsOrder
    return out


def restoreReferences(portal):
    """ iterate over all Dexterity Objs and restore as Dexterity Reference. """
    out = ''
    catalog = getToolByName(portal, "portal_catalog")
    # Seems that these newly created objs are not reindexed
    catalog.clearFindAndRebuild()
    results = catalog.searchResults(
        object_provides=IDexterityContent.__identifier__)

    for brain in results:
        obj = brain.getObject()

        # refs
        out += refs(obj)
        # backrefs
        out += backrefs(portal, obj)
        # order
        out += order(obj)

    return out


class ReferenceMigrator(object):

    def beforeChange_relatedItemsOrder(self):
        """ Store Archetype relations as target uids on the old archetype
            object to restore the order later.
            Because all relations to deleted objects will be lost, we iterate
            over all backref objects and store the relations of the backref
            object in advance.
            This is automatically called by Products.contentmigration.
        """
        # Relations UIDs:
        if not hasattr(self.old, "_relatedItemsOrder"):
            relatedItems = self.old.getRelatedItems()
            relatedItemsOrder = [item.UID() for item in relatedItems]
            self.old._relatedItemsOrder = PersistentList(relatedItemsOrder)

        # Backrefs Relations UIDs:
        reference_cat = getToolByName(self.old, REFERENCE_CATALOG)
        backrefs = reference_cat.getBackReferences(self.old,
                                                   relationship="relatesTo")
        backref_objects = map(lambda x: x.getSourceObject(), backrefs)
        for obj in backref_objects:
            if obj.portal_type != self.src_portal_type:
                continue
            if not hasattr(obj, "_relUids"):
                relatedItems = obj.getRelatedItems()
                relatedItemsOrder = [item.UID() for item in relatedItems]
                obj._relatedItemsOrder = PersistentList(relatedItemsOrder)

    def migrate_at_relatedItems(self):
        """ Store Archetype relations as target uids on the dexterity object
            for later restore. Backrelations are saved as well because all
            relation to deleted objects would be lost.
        """
        # Relations:
        relItems = self.old.getRelatedItems()
        relUids = [item.UID() for item in relItems]
        self.new._relatedItems = relUids

        # Backrefs:
        reference_catalog = getToolByName(self.old, REFERENCE_CATALOG)

        backrefs = [i.sourceUID for i in reference_catalog.getBackReferences(
            self.old, relationship="relatesTo")]
        self.new._backrefs = backrefs

        # Order:
        self.new._relatedItemsOrder = self.old._relatedItemsOrder


class ICustomMigrator(Interface):
    """Adapter implementer interface for custom migrators.
    Please note that you have to register named adapters in order to be able to
    register multiple adapters to the same adaptee.
    """
    def migrate(old, new):
        """Start the custom migraton.
        :param old: The old content object.
        :param new: The new content object.
        """


@implementer(ICustomMigrator)
@adapter(Interface)
class BaseCustomMigator(object):
    """Base custom migration class. Does nothing.

    You can use this as base class for your custom migrator adapters.
    You might register it to some specific orginal content interface.
    """
    def __init__(self, context):
        self.context = context

    def migrate(self, old, new):
        return


class ATCTContentMigrator(CMFItemMigrator, ReferenceMigrator):
    """Base for contentish ATCT
    """

    def __init__(self, *args, **kwargs):
        super(ATCTContentMigrator, self).__init__(*args, **kwargs)
        logger.info(
            "Migrating object %s" %
            '/'.join(self.old.getPhysicalPath())
        )

    def migrate_atctmetadata(self):
        field = self.old.getField('excludeFromNav')
        self.new.exclude_from_nav = field.get(self.old)

    def migrate_custom(self):
        """Get all ICustomMigrator registered migrators and run the migration.
        """
        for _, migrator in getAdapters((self.old, ), ICustomMigrator):
            migrator.migrate(self.old, self.new)


class ATCTFolderMigrator(CMFFolderMigrator, ReferenceMigrator):
    """Base for folderish ATCT
    """

    def __init__(self, *args, **kwargs):
        super(ATCTFolderMigrator, self).__init__(*args, **kwargs)
        logger.info(
            "Migrating object %s" %
            '/'.join(self.old.getPhysicalPath())
        )

    def migrate_atctmetadata(self):
        field = self.old.getField('excludeFromNav')
        self.new.exclude_from_nav = field.get(self.old)

    def migrate_custom(self):
        """Get all ICustomMigrator registered migrators and run the migration.
        """
        for _, migrator in getAdapters((self.old, ), ICustomMigrator):
            migrator.migrate(self.old, self.new)


class DocumentMigrator(ATCTContentMigrator):

    src_portal_type = 'Document'
    src_meta_type = 'ATDocument'
    dst_portal_type = 'Document'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
        field = self.old.getField('text')
        mime_type = field.getContentType(self.old)
        raw_text = safe_unicode(field.getRaw(self.old))
        if raw_text.strip() == '':
            return
        richtext = RichTextValue(raw=raw_text, mimeType=mime_type,
                                 outputMimeType='text/x-html-safe')
        self.new.text = richtext


def migrate_documents(portal):
    return migrate(portal, DocumentMigrator)


class FileMigrator(ATCTContentMigrator):

    src_portal_type = 'File'
    src_meta_type = 'ATFile'
    dst_portal_type = 'File'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
        old_file = self.old.getField('file').get(self.old)
        filename = safe_unicode(old_file.filename)
        namedblobfile = NamedBlobFile(contentType=old_file.content_type,
                                      data=old_file.data,
                                      filename=filename)
        self.new.file = namedblobfile


def migrate_files(portal):
    return migrate(portal, FileMigrator)


class BlobFileMigrator(FileMigrator):

    src_portal_type = 'File'
    src_meta_type = 'ATBlob'
    dst_portal_type = 'File'
    dst_meta_type = None  # not used


def migrate_blobfiles(portal):
    return migrate(portal, BlobFileMigrator)


class ImageMigrator(ATCTContentMigrator):

    src_portal_type = 'Image'
    src_meta_type = 'ATImage'
    dst_portal_type = 'Image'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
        old_image = self.old.getField('image').get(self.old)
        if old_image == '':
            return
        filename = safe_unicode(old_image.filename)
        namedblobimage = NamedBlobImage(data=old_image.data,
                                        filename=filename)
        self.new.image = namedblobimage


def migrate_images(portal):
    return migrate(portal, ImageMigrator)


class BlobImageMigrator(ImageMigrator):

    src_portal_type = 'Image'
    src_meta_type = 'ATBlob'
    dst_portal_type = 'Image'
    dst_meta_type = None  # not used


def migrate_blobimages(portal):
    return migrate(portal, BlobImageMigrator)


class LinkMigrator(ATCTContentMigrator):

    src_portal_type = 'Link'
    src_meta_type = 'ATLink'
    dst_portal_type = 'Link'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
        remoteUrl = self.old.getField('remoteUrl').get(self.old)
        self.new.remoteUrl = remoteUrl


def migrate_links(portal):
    return migrate(portal, LinkMigrator)


class NewsItemMigrator(DocumentMigrator):

    src_portal_type = 'News Item'
    src_meta_type = 'ATNewsItem'
    dst_portal_type = 'News Item'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
        # migrate the text
        super(NewsItemMigrator, self).migrate_schema_fields()

        # migrate the rest of the Schema
        old_image = self.old.getField('image').get(self.old)
        if old_image == '':
            return
        filename = safe_unicode(old_image.filename)
        old_image_data = old_image.data
        if safe_hasattr(old_image_data, 'data'):
            old_image_data = old_image_data.data
        namedblobimage = NamedBlobImage(data=old_image_data,
                                        filename=filename)
        self.new.image = namedblobimage
        self.new.image_caption = safe_unicode(
            self.old.getField('imageCaption').get(self.old))


def migrate_newsitems(portal):
    return migrate(portal, NewsItemMigrator)


class BlobNewsItemMigrator(NewsItemMigrator):
    """ Migrator for NewsItems with blobs based on the implementation in
        https://github.com/plone/plone.app.blob/pull/2
    """

    src_portal_type = 'News Item'
    src_meta_type = 'ATBlobContent'
    dst_portal_type = 'News Item'
    dst_meta_type = None  # not used


def migrate_blobnewsitems(portal):
    return migrate(portal, BlobNewsItemMigrator)


class FolderMigrator(ATCTFolderMigrator):

    src_portal_type = 'Folder'
    src_meta_type = 'ATFolder'
    dst_portal_type = 'Folder'
    dst_meta_type = None  # not used

    def beforeChange_migrate_layout(self):
        if self.old.getLayout() == 'atct_album_view':
            self.old.setLayout('folder_album_view')


def migrate_folders(portal):
    return migrate(portal, FolderMigrator)


class CollectionMigrator(DocumentMigrator):
    """Migrator for at-based collections provided by plone.app.collection
    to
    """

    src_portal_type = 'Collection'
    src_meta_type = 'Collection'
    dst_portal_type = 'Collection'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
        # migrate the richtext
        super(CollectionMigrator, self).migrate_schema_fields()

        # migrate the rest of the schema into the behavior
        wrapped = ICollection(self.new)
        wrapped.query = self.old.query
        wrapped.sort_on = self.old.sort_on
        wrapped.sort_reversed = self.old.sort_reversed
        wrapped.limit = self.old.limit
        wrapped.customViewFields = self.old.customViewFields


def migrate_collections(portal):
    return migrate(portal, CollectionMigrator)


class EventMigrator(ATCTContentMigrator):
    """Migrate both Products.ContentTypes & plone.app.event.at Events"""

    src_portal_type = 'Event'
    src_meta_type = 'ATEvent'
    dst_portal_type = 'Event'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
        old_start = self.old.getField('startDate').get(self.old)
        old_end = self.old.getField('endDate').get(self.old)
        old_location = self.old.getField('location').get(self.old)
        old_attendees = self.old.getField('attendees').get(self.old)
        old_eventurl = self.old.getField('eventUrl').get(self.old)
        old_contactname = self.old.getField('contactName').get(self.old)
        old_contactemail = self.old.getField('contactEmail').get(self.old)
        old_contactphone = self.old.getField('contactPhone').get(self.old)
        old_text_field = self.old.getField('text')
        raw_text = safe_unicode(old_text_field.getRaw(self.old))
        mime_type = old_text_field.getContentType(self.old)
        if raw_text.strip() == '':
            raw_text = ''
        old_richtext = RichTextValue(raw=raw_text, mimeType=mime_type,
                                     outputMimeType='text/x-html-safe')

        wholeDay = None
        if self.old.getField('wholeDay'):
            wholeDay = self.old.getField('wholeDay').get(self.old)

        openEnd = None
        if self.old.getField('openEnd'):
            openEnd = self.old.getField('openEnd').get(self.old)

        recurrence = None
        if self.old.getField('recurrence'):
            recurrence = self.old.getField('recurrence').get(self.old)

        if self.old.getField('timezone'):
            old_timezone = self.old.getField('timezone').get(self.old)
        else:
            old_timezone = default_timezone(fallback='UTC')

        # IEventBasic
        self.new.start = datetime_fixer(old_start.asdatetime(), old_timezone)
        self.new.end = datetime_fixer(old_end.asdatetime(), old_timezone)

        if wholeDay is not None:
            self.new.whole_day = wholeDay  # IEventBasic
        if openEnd is not None:
            self.new.open_end = openEnd  # IEventBasic
        if recurrence is not None:
            self.new.recurrence = recurrence  # IEventRecurrence

        self.new.location = old_location  # IEventLocation
        self.new.attendees = old_attendees  # IEventAttendees
        self.new.event_url = old_eventurl  # IEventContact
        self.new.contact_name = old_contactname  # IEventContact
        self.new.contact_email = old_contactemail  # IEventContact
        self.new.contact_phone = old_contactphone  # IEventContact
        # Copy the entire richtext object, not just it's representation
        self.new.text = old_richtext


def migrate_events(portal):
    migrate(portal, DXOldEventMigrator)
    migrate(portal, EventMigrator)
    migrate(portal, DXEventMigrator)


def makeCustomATMigrator(context, src_type, dst_type, fields_mapping, is_folderish=False, dry_run=False):
    """ generate a migrator for the given at-based folderish portal type """

    base_class = ATCTContentMigrator
    if is_folderish:
        base_class = ATCTFolderMigrator

    class CustomATMigrator(base_class):

        src_portal_type = src_type
        dst_portal_type = dst_type
        dry_run_mode = dry_run

        def migrate_schema_fields(self):
            for fields_dict in fields_mapping:
                at_fieldname = fields_dict.get('AT_field_name')
                at_fieldtype = fields_dict.get('AT_field_type')
                dx_fieldname = fields_dict.get('DX_field_name')
                migration_field_method = migrate_simplefield
                if at_fieldtype in FIELDS_MAPPING:
                    migration_field_method = FIELDS_MAPPING[at_fieldtype]
                migration_field_method(src_obj=self.old,
                                       dst_obj=self.new,
                                       src_fieldname=at_fieldname,
                                       dst_fieldname=dx_fieldname)

        def last_migrate_check(self):
            """
            BBB to be checked
            if there is an error with the fields, an exception will be raised.
            """
            if self.dry_run_mode:
                view = getMultiAdapter((self.new, self.new.REQUEST), name="view")
                view()

    return CustomATMigrator


def migrateCustomAT(fields_mapping, src_type, dst_type, dry_run=False):
    """
    Try to get types infos from archetype_tool, then set a migrator an pass it given values.
    There is a dry_run mode that allows to check the success of a migration without committing.
    """
    portal = getSite()
    archetype_tool = getToolByName(portal, 'archetype_tool', None)
    src_type_infos = None
    if not archetype_tool:
        return
    # get the src meta_type from the portal_type
    portal_types = getToolByName(portal, 'portal_types')
    src_meta_type = getattr(portal_types, src_type).content_meta_type
    # lookup registered type in archetype_tool with
    # meta_type because several portal_types can use same meta_type
    for info in archetype_tool.listRegisteredTypes():
        if info.get('meta_type') == src_meta_type:
            src_type_infos = info
    is_folderish = src_type_infos.get('klass').isPrincipiaFolderish
    # TODO : to be removed when this parameter comes from the view
    dry_run = True
    migrator = makeCustomATMigrator(context=portal,
                                    src_type=src_type,
                                    dst_type=dst_type,
                                    fields_mapping=fields_mapping,
                                    is_folderish=is_folderish,
                                    dry_run=dry_run)
    if migrator:
        migrator.src_meta_type = src_meta_type
        migrator.dst_meta_type = ''
        walker_settings = {'portal': portal,
                           'migrator': migrator,
                           'src_portal_type': src_type,
                           'dst_portal_type': dst_type,
                           'src_meta_type': src_meta_type,
                           'dst_meta_type': '',
                           'use_savepoint': True}
        if dry_run:
            tools = getMultiAdapter((portal, portal.REQUEST), name=u'plone_tools')
            portal_catalog = tools.catalog()
            #BBB search_limit doesn't seems working
            test_search = portal_catalog(portal_type=src_type, search_limit=1)
            if test_search:
                walker_settings['query'] = {'UID': test_search[0].UID}
        walker = CustomQueryWalker(**walker_settings)
        walker.go()
        walker_infos = {'errors': walker.errors,
                        'msg': walker.getOutput().splitlines(),
                        'counter': walker.counter}
        for error in walker.errors:
            logger.error(error.get('message'))
        if dry_run:
            transaction.abort()
        return walker_infos
