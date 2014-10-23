# -*- coding: utf-8 -*-
from Products.contentmigration.basemigrator.migrator import CMFItemMigrator
from Products.contentmigration.basemigrator.walker import CatalogWalker
from plone.app.contenttypes.interfaces import IEvent
from plone.app.contenttypes.migration import datetime_fixer
from plone.event.utils import default_timezone
from zope.annotation.interfaces import IAnnotations
from zope.component.hooks import getSite


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
