# -*- coding: utf-8 -*-
"""
Migrating ATContentTypes to plone.app.contenttypes objects.

This module imports from Product.contentmigration on which we depend
only in the setuptools extra_requiers [migrate_atct]. Importing this
module will only work if Products.contentmigration is installed so make sure
you catch ImportErrors
"""
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.app.contenttypes.migration.dxmigration import DXEventMigrator
from plone.app.contenttypes.migration.dxmigration import DXOldEventMigrator
from plone.app.contenttypes.migration.field_migrators import FIELDS_MAPPING
from plone.app.contenttypes.migration.field_migrators import migrate_blobimagefield  # noqa
from plone.app.contenttypes.migration.field_migrators import migrate_datetimefield  # noqa
from plone.app.contenttypes.migration.field_migrators import migrate_filefield
from plone.app.contenttypes.migration.field_migrators import migrate_imagefield
from plone.app.contenttypes.migration.field_migrators import migrate_richtextfield  # noqa
from plone.app.contenttypes.migration.field_migrators import migrate_simplefield  # noqa
from plone.app.contenttypes.migration.patches import patch_before_migration
from plone.app.contenttypes.migration.patches import undo_patch_after_migration
from plone.app.contenttypes.migration.utils import copy_contentrules
from plone.app.contenttypes.migration.utils import migrate_leadimage
from plone.app.contenttypes.migration.utils import migrate_portlets
from plone.app.contenttypes.migration.utils import move_comments
from plone.app.contenttypes.upgrades import LISTING_VIEW_MAPPING
from plone.app.dexterity.behaviors.nextprevious import INextPreviousToggle
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFCore.utils import getToolByName
from Products.contentmigration.basemigrator.migrator import CMFFolderMigrator
from Products.contentmigration.basemigrator.migrator import CMFItemMigrator
from Products.contentmigration.basemigrator.walker import CatalogWalker
from Products.contentmigration.walker import CustomQueryWalker
from Acquisition import aq_base
from zExceptions import NotFound
from zope.component import adapter
from zope.component import getAdapters
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import Interface

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
            'Migrating {0} {1}'.format(
                self.old.portal_type,
                '/'.join(self.old.getPhysicalPath())
            )
        )

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
        if field:
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
            'Migrating {0} {1}'.format(
                self.old.portal_type,
                '/'.join(self.old.getPhysicalPath()))
        )

    def beforeChange_store_comments_on_portal(self):
        """Comments from plone.app.discussion are lost when the
           old object is renamed...
           We save the comments in a safe place..."""
        portal = getToolByName(self.old, 'portal_url').getPortalObject()
        move_comments(self.old, portal)

    def migrate_atctmetadata(self):
        field = self.old.getField('excludeFromNav')
        if field:
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

    def migrate_nextprevious(self):
        if self.old.getNextPreviousEnabled():
            if INextPreviousToggle.providedBy(self.new):
                self.new.nextPreviousEnabled = True

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
        old_layout = getattr(aq_base(self.old), 'layout', None)
        if old_layout:
            default_page = getattr(aq_base(self.old), 'default_page', None)
            try:
                # Delete old-style layout attribute.
                del self.new.layout
            except AttributeError:
                pass
            # always copy over the layout, transform if necessary
            self.new.setLayout(LISTING_VIEW_MAPPING.get(old_layout, old_layout))  # noqa
            if default_page:
                # any defaultPage is switched of by setLayout
                # and needs to set again if it was directly on the object
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

    def migrate_schema_fields(self):
        migrate_richtextfield(self.old, self.new, 'text', 'text')
        wrapped_new = ICollection(self.new)
        # using migrate_simplefield on 'query' returns the ContentListing obj
        wrapped_new.query = self.old.query
        migrate_simplefield(self.old, wrapped_new, 'sort_on', 'sort_on')
        migrate_simplefield(
            self.old, wrapped_new, 'sort_reversed', 'sort_reversed')
        migrate_simplefield(self.old, wrapped_new, 'limit', 'limit')
        migrate_simplefield(
            self.old, wrapped_new, 'customViewFields', 'customViewFields')

    def last_migrate_layout(self):
        """Migrate the layout (view method).

        This needs to be done last, as otherwise our changes may get overriden
        by a later call to migrate_properties.
        """
        old_layout = self.old.getLayout() or getattr(self.old, 'layout', None)
        if old_layout:
            try:
                # Delete old-style layout attribute.
                del self.new.layout
            except AttributeError:
                pass
            self.new.setLayout(LISTING_VIEW_MAPPING.get(old_layout, old_layout))  # noqa


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


def makeCustomATMigrator(
    context,
    src_type,
    dst_type,
    fields_mapping,
    is_folderish=False,
    dry_run=False
):
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
                dx_fieldname = fields_dict.get('DX_field_name')
                dx_fieldtype = fields_dict.get('DX_field_type')
                migration_field_method = fields_dict.get('field_migrator')
                if not migration_field_method:
                    if dx_fieldtype in FIELDS_MAPPING:
                        # Richtext, Image and File have custom migraton_methods
                        migration_field_method = FIELDS_MAPPING[dx_fieldtype]
                    else:
                        migration_field_method = migrate_simplefield
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
                view = getMultiAdapter(
                    (self.new, self.new.REQUEST), name='view')
                view()

    return CustomATMigrator


def migrateCustomAT(fields_mapping,
                    src_type,
                    dst_type,
                    dry_run=False,
                    patch_linkintegrity=False,
                    patch_searchabletext=False,
                    ):
    """
    Try to get types infos from archetype_tool, then set a migrator and pass it
    given values. There is a dry_run mode that allows to check the success of
    a migration without committing.
    """
    portal = getSite()

    # Patch various things that make migration harder
    (link_integrity,
     queue_indexing,
     patch_searchabletext) = patch_before_migration(patch_searchabletext)

    # if the type still exists get the src_meta_type from the portal_type
    portal_types = getToolByName(portal, 'portal_types')
    fti = portal_types.get(src_type, None)
    # Check if the fti was removed or replaced by a DX-implementation
    if fti is None or IDexterityFTI.providedBy(fti):
        # Get the needed info from an instance of the type
        catalog = portal.portal_catalog
        brains = catalog(portal_type=src_type, sort_limit=1)
        if not brains:
            # no item? assume stuff
            is_folderish = False
            src_meta_type = src_type
        else:
            try:
                src_obj = brains[0].getObject()
            except (KeyError, NotFound):
                logger.error(
                    'Could not find the object for brain at %s',
                    brains[0].getURL())
                return
            if IDexterityContent.providedBy(src_obj):
                logger.error(
                    '%s should not be dexterity object!',
                    src_obj.absolute_url())
            is_folderish = getattr(src_obj, 'isPrincipiaFolderish', False)
            src_meta_type = src_obj.meta_type
    else:
        # Get info from at-fti
        src_meta_type = fti.content_meta_type
        archetype_tool = getToolByName(portal, 'archetype_tool', None)
        for info in archetype_tool.listRegisteredTypes():
            # lookup registered type in archetype_tool with meta_type
            # because several portal_types can use same meta_type
            if info.get('meta_type') == src_meta_type:
                klass = info.get('klass', None)
                is_folderish = klass.isPrincipiaFolderish

    migrator = makeCustomATMigrator(context=portal,
                                    src_type=src_type,
                                    dst_type=dst_type,
                                    fields_mapping=fields_mapping,
                                    is_folderish=is_folderish,
                                    dry_run=dry_run)
    walker_infos = None
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
            walker_settings['limit'] = 1
        walker = CustomQueryWalker(**walker_settings)
        walker.go()
        walker_infos = {'errors': walker.errors,
                        'msg': walker.getOutput().splitlines(),
                        'counter': walker.counter}
        for error in walker.errors:
            logger.error(error.get('message'))
        if dry_run:
            transaction.abort()

    # Revert to the original state
    undo_patch_after_migration(
        link_integrity, queue_indexing, patch_searchabletext)

    return walker_infos
