# -*- coding: utf-8 -*-
from Products.contentmigration.basemigrator.walker import CatalogWalker
from Products.contentmigration.basemigrator.migrator import CMFItemMigrator
from plone.app.contenttypes.interfaces import IEvent
from plone.event.interfaces import IEventAccessor
from zope.annotation.interfaces import IAnnotations
from zope.component.hooks import getSite
from zope.lifecycleevent import ObjectModifiedEvent
from zope.event import notify
from plone.event.utils import default_timezone


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
    # Re-import event-profile to get newest Event type
    context.runAllImportStepsFromProfile(
        'profile-plone.app.contenttypes:event',
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
        newacc = IEventAccessor(self.new)
        newacc.start = self.old.start_date
        newacc.end = self.old.end_date
        newacc.timezone = str(self.old.start_date.tzinfo) \
            if self.old.start_date.tzinfo \
            else default_timezone(fallback='UTC')

        if hasattr(self.old, 'location'):
            newacc.location = self.old.location
        if hasattr(self.old, 'attendees'):
            newacc.attendees = tuple(self.old.attendees.splitlines())
        if hasattr(self.old, 'event_url'):
            newacc.event_url = self.old.event_url
        if hasattr(self.old, 'contact_name'):
            newacc.contact_name = self.old.contact_name
        if hasattr(self.old, 'contact_email'):
            newacc.contact_email = self.old.contact_email
        if hasattr(self.old, 'contact_phone'):
            newacc.contact_phone = self.old.contact_phone
        if hasattr(self.old, 'text'):
            # Copy the entire richtext object, not just it's representation
            self.new.text = self.old.text

        # Trigger ObjectModified, so timezones can be fixed up.
        notify(ObjectModifiedEvent(self.new))


class DXEventMigrator(ContentMigrator):
    """Migrator for plone.app.event.dx events"""

    src_portal_type = 'plone.app.event.dx.event'
    src_meta_type = 'Dexterity Item'
    dst_portal_type = 'Event'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
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
        # The old behavior for the rich text field does not exist an more.
        # Look up the old value directly from the Annotation storage
        # Copy the entire richtext object, not just it's representation
        annotations = IAnnotations(self.old)
        old_text = annotations.get(
            'plone.app.event.dx.behaviors.IEventSummary.text', None)
        self.new.text = old_text

        # Trigger ObjectModified, so timezones can be fixed up.
        notify(ObjectModifiedEvent(self.new))
