# -*- coding: utf-8 -*-
'''
Migrating ATContentTypes to plone.app.contenttypes objects.

This module imports from Product.contentmigration on which we depend
only in the setuptools extra_requiers [migrate_atct]. Importing this
module will only work if Products.contentmigration is installed so make sure
you catch ImportErrors
'''
from Products.CMFCore.utils import getToolByName
from Products.contentmigration.basemigrator.migrator import CMFFolderMigrator
from Products.contentmigration.basemigrator.migrator import CMFItemMigrator
from Products.contentmigration.basemigrator.walker import CatalogWalker
from Products.contentmigration.walker import CustomQueryWalker
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.app.contenttypes.migration.dxmigration import DXEventMigrator
from plone.app.contenttypes.migration.dxmigration import DXOldEventMigrator
from plone.app.contenttypes.migration.utils import copy_contentrules
from plone.app.contenttypes.migration.utils import migrate_leadimage
from plone.app.contenttypes.migration.utils import move_comments
from plone.app.contenttypes.migration.utils import migrate_portlets
from plone.app.contenttypes.migration.field_migrators import FIELDS_MAPPING
from plone.app.contenttypes.migration.field_migrators import \
    migrate_datetimefield
from plone.app.contenttypes.migration.field_migrators import migrate_filefield
from plone.app.contenttypes.migration.field_migrators import migrate_imagefield
from plone.app.contenttypes.migration.field_migrators import \
    migrate_blobimagefield
from plone.app.contenttypes.migration.field_migrators import \
    migrate_richtextfield
from plone.app.contenttypes.migration.field_migrators import \
    migrate_simplefield
from plone.app.contenttypes.upgrades import LISTING_VIEW_MAPPING
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import adapter
from zope.component import getAdapters
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.interface import Interface
from zope.interface import implementer
import logging
import transaction

logger = logging.getLogger(__name__)


def migrate(portal, migrator):
    """return a CatalogWalker instance in order
    to have its output after migration"""
    walker = CatalogWalker(portal, migrator)()
    return walker


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


class ATCTContentMigrator(CMFItemMigrator):
    """Base for contentish ATCT
    """

    def __init__(self, *args, **kwargs):
        super(ATCTContentMigrator, self).__init__(*args, **kwargs)
        logger.info(
            "Migrating {0}".format(
                '/'.join(self.old.getPhysicalPath())))

    def beforeChange_store_default_page(self):
        """If the item is the default page store that info to set it again.

        Products.CMFDynamicViewFTI.browserdefault.check_default_page
        would unset the default page during the migration.
        """
        context_state = getMultiAdapter(
            (self.old, self.old.REQUEST), name=u'plone_context_state')
        if context_state.is_default_page():
            setattr(self.old, '_migration_is_default_page', True)

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

    def last_migrate_default_page(self):
        """If the item was the default page set it again."""
        if getattr(self.old, '_migration_is_default_page', False):
            parent = self.new.__parent__
            parent.setDefaultPage(self.new.id)


class ATCTFolderMigrator(CMFFolderMigrator):
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

    def last_migrate_layout(self):
        """Migrate the layout (view method).

        This needs to be done last, as otherwise our changes in
        migrate_criteria may get overriden by a later call to
        migrate_properties.
        """
        old_layout = self.old.getLayout() or getattr(self.old, 'layout', None)
        if old_layout in LISTING_VIEW_MAPPING.keys():
            default_page = self.old.getDefaultPage() or \
                getattr(self.old, 'default_page')
            self.new.setLayout(LISTING_VIEW_MAPPING[old_layout])
            if default_page:
                # any defaultPage is switched of by setLayout
                # and needs to set again
                self.new.setDefaultPage(default_page)


class DocumentMigrator(ATCTContentMigrator):

    src_portal_type = 'Document'
    src_meta_type = 'ATDocument'
    dst_portal_type = 'Document'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
        migrate_richtextfield(self.old, self.new, 'text', 'text')


def migrate_documents(portal):
    return migrate(portal, DocumentMigrator)


class FileMigrator(ATCTContentMigrator):

    src_portal_type = 'File'
    src_meta_type = 'ATFile'
    dst_portal_type = 'File'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
        migrate_filefield(self.old, self.new, 'file', 'file')


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
        migrate_imagefield(self.old, self.new, 'image', 'image')


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
        migrate_simplefield(self.old, self.new, 'remoteUrl', 'remoteUrl')


def migrate_links(portal):
    return migrate(portal, LinkMigrator)


class NewsItemMigrator(ATCTContentMigrator):

    src_portal_type = 'News Item'
    src_meta_type = 'ATNewsItem'
    dst_portal_type = 'News Item'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
        migrate_richtextfield(self.old, self.new, 'text', 'text')
        migrate_imagefield(self.old, self.new, 'image', 'image')
        migrate_simplefield(self.old, self.new, 'imageCaption', 'imageCaption')


def migrate_newsitems(portal):
    return migrate(portal, NewsItemMigrator)


class BlobNewsItemMigrator(ATCTContentMigrator):
    """ Migrator for NewsItems with blobs based on the implementation in
        https://github.com/plone/plone.app.blob/pull/2
    """

    src_portal_type = 'News Item'
    src_meta_type = 'ATBlobContent'
    dst_portal_type = 'News Item'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
        migrate_richtextfield(self.old, self.new, 'text', 'text')
        migrate_blobimagefield(self.old, self.new, 'image', 'image')
        migrate_simplefield(self.old, self.new, 'imageCaption', 'imageCaption')


def migrate_blobnewsitems(portal):
    return migrate(portal, BlobNewsItemMigrator)


class FolderMigrator(ATCTFolderMigrator):

    src_portal_type = 'Folder'
    src_meta_type = 'ATFolder'
    dst_portal_type = 'Folder'
    dst_meta_type = None  # not used

    def beforeChange_migrate_layout(self):
        if self.old.getLayout() == 'atct_album_view':
            self.old.setLayout('album_view')


def migrate_folders(portal):
    return migrate(portal, FolderMigrator)


class CollectionMigrator(ATCTContentMigrator):
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
        migrate_richtextfield(self.old, self.new, 'text', 'text')
        wrapped = ICollection(self.new)
        # using migrate_simplefield on 'query' returns the ContentListing obj
        wrapped.query = self.old.query
        migrate_simplefield(self.old, wrapped, 'sort_on', 'sort_on')
        migrate_simplefield(
            self.old, wrapped, 'sort_reversed', 'sort_reversed')
        migrate_simplefield(self.old, wrapped, 'limit', 'limit')
        migrate_simplefield(
            self.old, wrapped, 'customViewFields', 'customViewFields')

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
        migrate_datetimefield(self.old, self.new, 'startDate', 'start')
        migrate_datetimefield(self.old, self.new, 'endDate', 'end')
        migrate_richtextfield(self.old, self.new, 'text', 'text')
        migrate_simplefield(self.old, self.new, 'location', 'location')
        migrate_simplefield(self.old, self.new, 'attendees', 'attendees')
        migrate_simplefield(self.old, self.new, 'eventUrl', 'event_url')
        migrate_simplefield(self.old, self.new, 'contactName', 'contact_name')
        migrate_simplefield(
            self.old, self.new, 'contactEmail', 'contact_email')
        migrate_simplefield(
            self.old, self.new, 'contactPhone', 'contact_phone')
        migrate_simplefield(self.old, self.new, 'wholeDay', 'whole_day')
        migrate_simplefield(self.old, self.new, 'openEnd', 'open_end')
        migrate_simplefield(self.old, self.new, 'recurrence', 'recurrence')


def migrate_events(portal):
    migrate(portal, DXOldEventMigrator)
    migrate(portal, EventMigrator)
    migrate(portal, DXEventMigrator)
