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
from copy import deepcopy
from persistent.list import PersistentList
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.app.contenttypes.migration import datetime_fixer
from plone.app.contenttypes.migration.dxmigration import DXEventMigrator
from plone.app.contenttypes.migration.dxmigration import DXOldEventMigrator
from plone.app.contenttypes.migration.utils import add_portlet
from plone.app.contenttypes.migration.utils import copy_contentrules
from plone.app.contenttypes.migration.utils import move_comments
from plone.app.contenttypes.migration.utils import migrate_leadimage
from plone.app.contenttypes.utils import DEFAULT_TYPES
from plone.app.textfield.value import RichTextValue
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.interfaces import IDexterityContent
from plone.event.utils import default_timezone
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.portlets.constants import CONTEXT_BLACKLIST_STATUS_KEY
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from z3c.relationfield import RelationValue
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.component import getAdapters
from zope.component import getMultiAdapter
from zope.component import getSiteManager
from zope.component import getUtility
from zope.interface import Interface
from zope.interface import implementer
from zope.intid.interfaces import IIntIds

import logging
logger = logging.getLogger(__name__)


def migrate(portal, migrator):
    """return a CatalogWalker instance in order
    to have its output after migration"""
    walker = CatalogWalker(portal, migrator)()
    return walker


def migrate_portlets(src_obj, dst_obj):
    """Copy portlets for all available portletmanagers from one object
    to another.
    Also takes blocked portlet settings into account, keeps hidden portlets
    hidden and skips broken assignments.
    """

    # also take custom portlet managers into account
    managers = [reg.name for reg in getSiteManager().registeredUtilities()
                if reg.provided == IPortletManager]
    # faster, but no custom managers
    # managers = [u'plone.leftcolumn', u'plone.rightcolumn']

    # copy information which categories are hidden for which manager
    blacklist_status = IAnnotations(src_obj).get(
        CONTEXT_BLACKLIST_STATUS_KEY, None)
    if blacklist_status is not None:
        IAnnotations(dst_obj)[CONTEXT_BLACKLIST_STATUS_KEY] = \
            deepcopy(blacklist_status)

    # copy all portlet assignments (visibilty is stored as annotation
    # on the assignments and gets copied here too)
    for manager in managers:
        column = getUtility(IPortletManager, manager)
        mappings = getMultiAdapter((src_obj, column),
                                   IPortletAssignmentMapping)
        for key, assignment in mappings.items():
            # skip possibly broken portlets here
            if not hasattr(assignment, '__Broken_state__'):
                add_portlet(dst_obj, assignment, key, manager)
            else:
                logger.warn(u'skipping broken portlet assignment {0} '
                            'for manager {1}'.format(key, manager))


def restore_refs(obj):
    """Restore references stored in the attribute _relatedItems.
    """
    intids = getUtility(IIntIds)
    try:
        if not getattr(obj, 'relatedItems', None):
            obj.relatedItems = PersistentList()

        elif type(obj.relatedItems) != type(PersistentList()):
            obj.relatedItems = PersistentList(obj.relatedItems)

        for uuid in obj._relatedItems:
            to_obj = uuidToObject(uuid)
            to_id = intids.getId(to_obj)
            obj.relatedItems.append(RelationValue(to_id))
            logger.info('Restored Relation from %s to %s' % (obj, to_obj))
    except AttributeError:
        pass


def restore_backrefs(portal, obj):
    """Restore backreferences stored in the attribute _backrefs.
    """
    intids = getUtility(IIntIds)
    uid_catalog = getToolByName(portal, 'uid_catalog')
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
            logger.info(
                'Restored BackRelation from %s to %s' % (backrefobj, obj))
    except AttributeError:
        pass


def restore_reforder(obj):
    """Restore order of references stored in the attribute _relatedItemsOrder.
    """
    if not hasattr(obj, '_relatedItemsOrder'):
        # Nothing to do
        return
    relatedItemsOrder = obj._relatedItemsOrder
    uid_position_map = dict([(y, x) for x, y in enumerate(relatedItemsOrder)])
    key = lambda rel: uid_position_map.get(rel.to_object.UID(), 0)
    obj.relatedItems = sorted(obj.relatedItems, key=key)


def cleanup_stored_refs(obj):
    """Cleanup new dx item."""
    if safe_hasattr(obj, '_relatedItems'):
        del obj._relatedItems
    if safe_hasattr(obj, '_backrefs'):
        del obj._backrefs
    if safe_hasattr(obj, '_relatedItemsOrder'):
    del obj._relatedItemsOrder


def restoreReferences(portal,
                      migrate_references=True,
                      content_types=DEFAULT_TYPES):
    """Iterate over new Dexterity items and restore Dexterity References.
    """
    catalog = getToolByName(portal, "portal_catalog")
    results = catalog.searchResults(
        object_provides=IDexterityContent.__identifier__,
        portal_type=content_types)

    for brain in results:
        obj = brain.getObject()
        if migrate_references:
            restore_refs(obj)
            restore_backrefs(portal, obj)
            restore_reforder(obj)
        cleanup_stored_refs(obj)


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
            "Migrating {0}".format(
                '/'.join(self.old.getPhysicalPath())))

    def beforeChange_store_comments_on_portal(self):
        """Comments from plone.app.discussion are lost when the
           old object is renamed...
           We save the comments in a safe place..."""
        portal = getToolByName(self.old, 'portal_url').getPortalObject()
        move_comments(self.old, portal)

    def migrate_atctmetadata(self):
        field = self.old.getField('excludeFromNav')
        self.new.exclude_from_nav = field.get(self.old)

    def migrate_custom(self):
        """Get all ICustomMigrator registered migrators and run the migration.
        """
        for _, migrator in getAdapters((self.old,), ICustomMigrator):
            migrator.migrate(self.old, self.new)

    def migrate_portlets(self):
        migrate_portlets(self.old, self.new)

    def migrate_contentrules(self):
        copy_contentrules(self.old, self.new)

    def migrate_leadimage(self):
        migrate_leadimage(self.old, self.new)

    def last_migrate_comments(self):
        """Migrate the plone.app.discussion comments.
           Comments were stored on the portal, get them and
           Copy the conversations from old to new object."""
        portal = getToolByName(self.old, 'portal_url').getPortalObject()
        move_comments(portal, self.new)


class ATCTFolderMigrator(CMFFolderMigrator, ReferenceMigrator):
    """Base for folderish ATCT
    """

    def __init__(self, *args, **kwargs):
        super(ATCTFolderMigrator, self).__init__(*args, **kwargs)
        logger.info(
            "Migrating {}".format('/'.join(self.old.getPhysicalPath())))

    def beforeChange_store_comments_on_portal(self):
        """Comments from plone.app.discussion are lost when the
           old object is renamed...
           We save the comments in a safe place..."""
        portal = getToolByName(self.old, 'portal_url').getPortalObject()
        move_comments(self.old, portal)

    def migrate_atctmetadata(self):
        field = self.old.getField('excludeFromNav')
        self.new.exclude_from_nav = field.get(self.old)

    def migrate_custom(self):
        """Get all ICustomMigrator registered migrators and run the migration.
        """
        for _, migrator in getAdapters((self.old,), ICustomMigrator):
            migrator.migrate(self.old, self.new)

    def migrate_portlets(self):
        migrate_portlets(self.old, self.new)

    def migrate_contentrules(self):
        copy_contentrules(self.old, self.new)

    def migrate_leadimage(self):
        migrate_leadimage(self.old, self.new)

    def last_migrate_comments(self):
        """Migrate the plone.app.discussion comments.
           Comments were stored on the portal, get them and
           Copy the conversations from old to new object."""
        portal = getToolByName(self.old, 'portal_url').getPortalObject()
        move_comments(portal, self.new)


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

    view_methods_mapping = {
        'folder_listing': 'standard_view',
        'folder_summary_view': 'summary_view',
        'folder_full_view': 'all_content',
        'folder_tabular_view': 'tabular_view',
        'atct_album_view': 'thumbnail_view',
        'atct_topic_view': 'standard_view',
        }

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

    def last_migrate_layout(self):
        """Migrate the layout (view method).
        """
        old_layout = self.old.getLayout() or getattr(self.old, 'layout', None)
        layout = self.view_methods_mapping.get(old_layout)
        if layout:
            self.new.setLayout(layout)


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
