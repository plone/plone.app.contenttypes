# -*- coding: utf-8 -*-
from plone.app.contenttypes.interfaces import IEvent
from plone.dexterity.content import Item
from plone.dexterity.fti import DexterityFTI
from zope.interface import implementer


@implementer(IEvent)
class Event(Item):
    """Dummy subclass for old ``Event`` portal type
    """


def create1_0EventType(portal):
    """Recreate the old event type used in the 1.0 branch"""
    fti = DexterityFTI('Event')
    fti.title = 'Event'
    fti.description = 'Events can be shown in calendars.'
    fti.factory = 'Event'
    fti.add_view_expr = 'string:${folder_url}/++add++Event'
    fti.link_target = ''
    fti.link_target = ''
    fti.immediate_view = 'view'
    fti.global_allow = True
    fti.filter_content_types = True
    fti.allowed_content_types = []
    fti.allow_discussion = False
    fti.default_view = 'event_view'
    fti.view_methods = ('event_view', )
    fti.default_view_fallback = False
    fti.add_permission = 'plone.app.contenttypes.addEvent'
    fti.klass = 'plone.app.contenttypes.tests.oldtypes.Event'
    fti.behaviors = (
        'plone.app.contenttypes.interfaces.IEvent',
        'plone.app.dexterity.behaviors.metadata.IDublinCore',
        'plone.app.content.interfaces.INameFromTitle',
        'plone.app.dexterity.behaviors.discussion.IAllowDiscussion',
        'plone.app.dexterity.behaviors.exclfromnav.IExcludeFromNavigation',
        'plone.app.relationfield.behavior.IRelatedItems',
        'plone.app.versioningbehavior.behaviors.IVersionable',
    )
    fti.schema = None
    fti.model_source = """
<model xmlns="http://namespaces.plone.org/supermodel/schema"
       xmlns:indexer="http://namespaces.plone.org/supermodel/indexer"
       xmlns:i18n="http://xml.zope.org/namespaces/i18n"
       i18n:domain="plone">
    <schema>
      <field name="location" type="zope.schema.TextLine"
             indexer:searchable="true">
        <description />
        <required>False</required>
        <title i18n:translate="label_event_location">Event Location</title>
      </field>
      <field name="start_date" type="zope.schema.Datetime">
        <description />
        <title i18n:translate="label_event_start">Event Starts</title>
      </field>
      <field name="end_date" type="zope.schema.Datetime">
        <description />
        <title i18n:translate="label_event_end">Event Ends</title>
      </field>
      <field name="text" type="plone.app.textfield.RichText"
             indexer:searchable="true">
        <description />
        <required>False</required>
        <title i18n:translate="">Text</title>
      </field>
      <field name="attendees" type="zope.schema.Text"
             indexer:searchable="true">
        <description />
        <required>False</required>
        <title i18n:translate="label_event_attendees">Attendees</title>
      </field>
      <field name="event_url" type="zope.schema.TextLine">
        <description i18n:translate="help_url">
          Web address with more info about the event. Add http:// for external
          links.
        </description>
        <required>False</required>
        <title i18n:translate="event_more_information">Event URL</title>
      </field>
      <field name="contact_name" type="zope.schema.TextLine"
             indexer:searchable="true">
        <description />
        <required>False</required>
        <title i18n:translate="label_contact_name">Contact Name</title>
      </field>
      <field name="contact_email" type="zope.schema.TextLine">
        <description />
        <required>False</required>
        <title i18n:translate="label_contact_email">Contact E-mail</title>
      </field>
      <field name="contact_phone" type="zope.schema.TextLine">
        <description />
        <required>False</required>
        <title i18n:translate="label_contact_phone">Contact Phone</title>
      </field>
    </schema>
</model>"""
    fti.model_file = None  # Was plone.app.contenttypes.schema:event.xml

    if 'Event' in portal.portal_types:
        del portal.portal_types['Event']
    portal.portal_types._setObject('Event', fti)
    return fti
