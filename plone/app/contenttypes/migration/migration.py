# -*- coding: utf-8 -*-
'''
Migrating ATContentTypes to plone.app.contenttypes objects.

This module imports from Product.contentmigration on which we depend
only in the setuptools extra_requiers [migrate_atct]. Importing this
module will only work if Products.contentmigration is installed so make sure
you catch ImportErrors
'''
from Products.ATContentTypes.interfaces.interfaces import IATContentType
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode, safe_hasattr
from Products.contentmigration.basemigrator.migrator import CMFFolderMigrator
from Products.contentmigration.basemigrator.migrator import CMFItemMigrator
from Products.contentmigration.basemigrator.walker import CatalogWalker
from persistent.list import PersistentList
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.app.contenttypes.migration.dxmigration import DXEventMigrator
from plone.app.contenttypes.migration.dxmigration import DXOldEventMigrator
from plone.app.textfield.value import RichTextValue
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.interfaces import IDexterityContent
from plone.event.interfaces import IEventAccessor
from plone.event.utils import default_timezone
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from z3c.relationfield import RelationValue
from zope.component import adapter
from zope.component import getAdapters
from zope.component import getUtility
from zope.event import notify
from zope.interface import Interface
from zope.interface import implementer
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectModifiedEvent


import logging
logger = logging.getLogger(__name__)


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
        #order
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

    def migrate_relatedItems(self):
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
        if self.old.getField('timezone'):
            old_timezone = self.old.getField('timezone').get(self.old)
        else:
            old_timezone = default_timezone(fallback='UTC')

        acc = IEventAccessor(self.new)
        acc.start = old_start.asdatetime()  # IEventBasic
        acc.end = old_end.asdatetime()  # IEventBasic
        acc.timezone = old_timezone  # IEventBasic
        acc.location = old_location  # IEventLocation
        acc.attendees = old_attendees  # IEventAttendees
        acc.event_url = old_eventurl  # IEventContact
        acc.contact_name = old_contactname  # IEventContact
        acc.contact_email = old_contactemail  # IEventContact
        acc.contact_phone = old_contactphone  # IEventContact
        # Copy the entire richtext object, not just it's representation
        self.new.text = old_richtext

        # Trigger ObjectModified, so timezones can be fixed up.
        notify(ObjectModifiedEvent(self.new))


def migrate_events(portal):
    migrate(portal, DXOldEventMigrator)
    migrate(portal, EventMigrator)
    migrate(portal, DXEventMigrator)
