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
from plone.app.textfield.value import RichTextValue
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.interfaces import IDexterityContent
from plone.event.interfaces import IEventAccessor
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.event import notify
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectModifiedEvent


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
        # keep the _relatedItems to restore the order
        # del obj._relatedItems

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

    return out


def restoreReferencesOrder(portal):
    """ In obj._relatedItems is the correct order of references. Let's
        replace the ATReference (UID) by the new Dexterity Refeŕence.
        Then we have a list with ordered Refs and can replace
        obj.relatedItems."""
    out = ''
    catalog = getToolByName(portal, "portal_catalog")
    results = catalog.searchResults(
        object_provides=IDexterityContent.__identifier__)
    # Iteration on all dexterity objects
    for brain in results:
        obj = brain.getObject()
        if not getattr(obj, '_relatedItems', None):
            continue
        # In obj._relatedItems we have the right order.
        atRelItems = obj._relatedItems
        # Replace the AT Ref by the Dex. Ref
        for i in atRelItems:
            for rel in obj.relatedItems:
                if rel.to_object.UID() == i:
                    atRelItems[atRelItems.index(i)] = rel
                    break
        obj.relatedItems = atRelItems
        del obj._relatedItems
        out += str('%s ordered.' % obj)
    return out


class ReferenceMigrator(object):

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


class ATCTBaseMigrator(CMFItemMigrator, ReferenceMigrator):

    def migrate_atctmetadata(self):
        field = self.old.getField('excludeFromNav')
        self.new.exclude_from_nav = field.get(self.old)


class ATCTContentMigrator(ATCTBaseMigrator,
                          CMFItemMigrator,
                          ReferenceMigrator):
    """Base for contentish ATCT
    """


class ATCTFolderMigrator(ATCTBaseMigrator,
                         CMFFolderMigrator,
                         ReferenceMigrator):
    """Base for folderish ATCT
    """


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


class BlobFileMigrator(ATCTContentMigrator):

    src_portal_type = 'File'
    src_meta_type = 'ATBlob'
    dst_portal_type = 'File'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
        old_file = self.old.getField('file').get(self.old)
        filename = safe_unicode(old_file.filename)
        namedblobfile = NamedBlobFile(contentType=old_file.content_type,
                                      data=old_file.data,
                                      filename=filename)
        self.new.file = namedblobfile


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


class BlobImageMigrator(ATCTContentMigrator):

    src_portal_type = 'Image'
    src_meta_type = 'ATBlob'
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


class BlobNewsItemMigrator(DocumentMigrator):
    """ Migrator for NewsItems with blobs based on the implementation in
        https://github.com/plone/plone.app.blob/pull/2
    """

    src_portal_type = 'News Item'
    src_meta_type = 'ATBlobContent'
    dst_portal_type = 'News Item'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
        # migrate the text
        super(BlobNewsItemMigrator, self).migrate_schema_fields()

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


def migrate_blobnewsitems(portal):
    return migrate(portal, BlobNewsItemMigrator)


class FolderMigrator(ATCTFolderMigrator):

    src_portal_type = 'Folder'
    src_meta_type = 'ATFolder'
    dst_portal_type = 'Folder'
    dst_meta_type = None  # not used


def migrate_folders(portal):
    return migrate(portal, FolderMigrator)


class CollectionMigrator(DocumentMigrator):

    src_portal_type = 'Collection'
    src_meta_type = 'Collection'
    dst_portal_type = 'Collection'
    dst_meta_type = None  # not used


def migrate_collections(portal):
    return migrate(portal, CollectionMigrator)


class EventMigrator(ATCTContentMigrator):
    """
    """

    src_portal_type = 'Event'
    src_meta_type = 'ATEvent'
    dst_portal_type = 'Event'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
        # super(EventMigrator, self).migrate_schema_fields()

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

        acc = IEventAccessor(self.new)
        acc.start = old_start.asdatetime()  # IEventBasic
        acc.end = old_end.asdatetime()  # IEventBasic
        acc.timezone = 'UTC'  # IEventBasic
        acc.location = old_location  # IEventLocation
        acc.attendees = old_attendees  # IEventAttendees
        acc.event_url = old_eventurl  # IEventContact
        acc.contact_name = old_contactname  # IEventContact
        acc.contact_email = old_contactemail  # IEventContact
        acc.contact_phone = old_contactphone  # IEventContact
        acc.text = old_richtext.raw


class DXEventMigrator(CMFItemMigrator):
    """Migrator for plone.app.event.dx events"""
    #TODO: ReferenceMigrator?

    src_portal_type = 'plone.app.event.dx.event'
    src_meta_type = None
    dst_portal_type = 'Event'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
        from plone.app.event.dx.behaviors import IEventSummary

        oldacc = IEventAccessor(self.old)
        newacc = IEventAccessor(self.new)
        newacc.start = oldacc.start
        newacc.end = oldacc.end
        newacc.timezone = oldacc.timezone
        newacc.location = oldacc.location
        newacc.attendees = oldacc.attendees
        newacc.event_url = oldacc.event_url
        newacc.contact_name = oldacc.contact_name
        newacc.contact_email = oldacc.contact_email
        newacc.contact_phone = oldacc.contact_phone
        # Copy the entire richtext object, not just it's representation
        IEventSummary(self.new).text = IEventSummary(self.old).text

        # Trigger ObjectModified, so timezones can be fixed up.
        notify(ObjectModifiedEvent(self.new))


def migrate_events(portal):
    return migrate(portal, EventMigrator)
