# -*- coding: utf-8 -*-
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base
from Products.CMFCore.utils import getToolByName
from Products.contentmigration.basemigrator.migrator import CMFItemMigrator
from Products.contentmigration.basemigrator.walker import CatalogWalker
from plone.app.contenttypes.interfaces import IEvent
from plone.app.contenttypes.migration.field_migrators import datetime_fixer
from plone.app.contenttypes.migration.utils import HAS_MULTILINGUAL
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityFTI
from plone.event.utils import default_timezone
from zExceptions import NotFound
from zope.annotation.interfaces import IAnnotations
from zope.component.hooks import getSite
from zope.component import queryUtility

import importlib
import logging

logger = logging.getLogger(__name__)


def migrate(portal, migrator):
    """return a CatalogWalker instance in order
    to have its output after migration"""
    walker = CatalogWalker(portal, migrator)()
    return walker


class ContentMigrator(CMFItemMigrator):
    """Base for contentish DX
    """

    def migrate_atctmetadata(self):
        self.new.exclude_from_nav = self.old.exclude_from_nav


def migrate_to_pa_event(context):
    # Install plone.app.event
    context.runAllImportStepsFromProfile('profile-plone.app.event:default')
    # Re-import types to get newest Event type
    context.runImportStepFromProfile(
        'profile-plone.app.contenttypes:default',
        'typeinfo'
    )
    portal = getSite()
    migrate(portal, DXOldEventMigrator)


class DXOldEventMigrator(ContentMigrator):
    """Migrator for 1.0 plone.app.contenttypes DX events"""

    src_portal_type = 'Event'
    src_meta_type = 'Dexterity Item'
    dst_portal_type = 'Event'
    dst_meta_type = None  # not used

    def migrate(self):
        # Only migrate items using old Schema
        if IEvent.providedBy(self.old) and hasattr(self.old, 'start_date'):
            ContentMigrator.migrate(self)

    def migrate_schema_fields(self):
        timezone = str(self.old.start_date.tzinfo) \
            if self.old.start_date.tzinfo \
            else default_timezone(fallback='UTC')

        self.new.start = datetime_fixer(self.old.start_date, timezone)
        self.new.end = datetime_fixer(self.old.end_date, timezone)

        if hasattr(self.old, 'location'):
            self.new.location = self.old.location
        if hasattr(self.old, 'attendees'):
            self.new.attendees = tuple(self.old.attendees.splitlines())
        if hasattr(self.old, 'event_url'):
            self.new.event_url = self.old.event_url
        if hasattr(self.old, 'contact_name'):
            self.new.contact_name = self.old.contact_name
        if hasattr(self.old, 'contact_email'):
            self.new.contact_email = self.old.contact_email
        if hasattr(self.old, 'contact_phone'):
            self.new.contact_phone = self.old.contact_phone
        if hasattr(self.old, 'text'):
            # Copy the entire richtext object, not just it's representation
            self.new.text = self.old.text


class DXEventMigrator(ContentMigrator):
    """Migrator for plone.app.event.dx events"""

    src_portal_type = 'plone.app.event.dx.event'
    src_meta_type = 'Dexterity Item'
    dst_portal_type = 'Event'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
        self.new.start = datetime_fixer(self.old.start, self.old.timezone)
        self.new.end = datetime_fixer(self.old.end, self.old.timezone)
        self.new.whole_day = self.old.whole_day
        self.new.open_end = self.old.open_end
        self.new.recurrence = self.old.recurrence
        self.new.location = self.old.location
        self.new.attendees = self.old.attendees
        self.new.event_url = self.old.event_url
        self.new.contact_name = self.old.contact_name
        self.new.contact_email = self.old.contact_email
        self.new.contact_phone = self.old.contact_phone
        # The old behavior for the rich text field does not exist an more.
        # Look up the old value directly from the Annotation storage
        # Copy the entire richtext object, not just it's representation
        annotations = IAnnotations(self.old)
        old_text = annotations.get(
            'plone.app.event.dx.behaviors.IEventSummary.text', None)
        self.new.text = old_text


def get_old_class_name_string(obj):
    """Returns the current class name string."""
    return '{0}.{1}'.format(obj.__module__, obj.__class__.__name__)


def get_portal_type_name_string(obj):
    """Returns the klass-attribute of the fti."""
    fti = queryUtility(IDexterityFTI, name=obj.portal_type)
    if not fti:
        return False
    return fti.klass


def migrate_base_class_to_new_class(obj,
                                    indexes=None,
                                    old_class_name='',
                                    new_class_name='',
                                    migrate_to_folderish=False,
                                    ):
    if indexes is None:
        indexes = ['is_folderish', 'object_provides']
    if not old_class_name:
        old_class_name = get_old_class_name_string(obj)
    if not new_class_name:
        new_class_name = get_portal_type_name_string(obj)
        if not new_class_name:
            logger.warning(
                'The type {0} has no fti!'.format(obj.portal_type))
            return False

    was_item = not isinstance(obj, BTreeFolder2Base)
    if old_class_name != new_class_name:
        obj_id = obj.getId()
        module_name, class_name = new_class_name.rsplit('.', 1)
        module = importlib.import_module(module_name)
        new_class = getattr(module, class_name)

        # update obj class
        parent = obj.__parent__
        parent._delOb(obj_id)
        obj.__class__ = new_class
        parent._setOb(obj_id, obj)

    is_container = isinstance(obj, BTreeFolder2Base)

    if was_item and is_container or migrate_to_folderish and is_container:
        #  If Itemish becomes Folderish we have to update obj _tree
        BTreeFolder2Base._initBTrees(obj)

    # reindex
    obj.reindexObject(indexes)

    return True


def list_of_objects_with_changed_base_class(context):
    catalog = getToolByName(context, "portal_catalog")
    query = {'object_provides': IDexterityContent.__identifier__}
    if HAS_MULTILINGUAL and 'Language' in catalog.indexes():
        query['Language'] = 'all'
    for brain in catalog(query):
        try:
            obj = brain.getObject()
        except NotFound:
            logger.warn("Object {0} not found".format(brain.getPath()))
            continue
        if get_portal_type_name_string(obj) != get_old_class_name_string(obj):
            yield obj


def list_of_changed_base_class_names(context):
    """Returns list of class names that are not longer in portal_types."""
    changed_base_class_names = {}
    for obj in list_of_objects_with_changed_base_class(context):
        changed_base_class_name = get_old_class_name_string(obj)
        if changed_base_class_name not in changed_base_class_names:
            changed_base_class_names[changed_base_class_name] = 1
        else:
            changed_base_class_names[changed_base_class_name] += 1
    return changed_base_class_names
