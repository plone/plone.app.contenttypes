# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import safe_unicode
from datetime import datetime
from plone.app.contenttypes.migration.migration import migrate_filefield
from plone.app.contenttypes.migration.migration import migrate_imagefield
from plone.app.contenttypes.migration.migration import migrate_simplefield
from plone.app.contenttypes.migration.utils import installTypeIfNeeded
from plone.app.contenttypes.testing import \
    PLONE_APP_CONTENTTYPES_MIGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import applyProfile
from plone.app.testing import setRoles

import pytz
import os.path
import unittest2 as unittest


class MigrateFieldsTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_MIGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def tearDown(self):
        try:
            applyProfile(self.portal, 'plone.app.contenttypes:uninstall')
        except KeyError:
            pass

    def get_test_image_data(self):
        test_image_path = os.path.join(os.path.dirname(__file__), 'image.png')
        with open(test_image_path, 'rb') as test_image_file:
            test_image_data = test_image_file.read()
        return test_image_data

    def get_test_file_data(self):
        test_file_path = os.path.join(os.path.dirname(__file__), 'file.pdf')
        with open(test_file_path, 'rb') as test_file:
            test_file_data = test_file.read()
        return test_file_data

    def test_migrate_stringfield(self):
        # create content
        at_document_id = self.portal.invokeFactory('Document',
                                                   'foo',
                                                   title="Foo document")
        # register p.a.contenttypes profile
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        dx_document_id = self.portal.invokeFactory('Document',
                                                   'bar',
                                                   title="Bar document")
        at_document = self.portal[at_document_id]
        dx_document = self.portal[dx_document_id]
        migrate_simplefield(at_document, dx_document, 'title', 'title')
        self.assertEqual(dx_document.Title(), at_document.Title())

    def test_migrate_richtextfield(self):
        # create content
        at_document_id = self.portal.invokeFactory('Document',
                                                   'foo',
                                                   title="Foo document",
                                                   text="Some foo html text")
        # register p.a.contenttypes profile
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        dx_document_id = self.portal.invokeFactory('Document',
                                                   'bar',
                                                   title="Bar document")
        at_document = self.portal[at_document_id]
        dx_document = self.portal[dx_document_id]
        self.assertEqual(dx_document.text, None)
        migrate_simplefield(at_document, dx_document, 'text', 'text')
        self.assertEqual(dx_document.text, at_document.getText())

    def test_migrate_listfield(self):
        # create content
        at_document_id = self.portal.invokeFactory('Document',
                                                   'foo',
                                                   title="Foo document",
                                                   subject=['aaa', 'bbb'])
        # register p.a.contenttypes profile
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        dx_document_id = self.portal.invokeFactory('Document',
                                                   'bar',
                                                   title="Bar document")
        at_document = self.portal[at_document_id]
        dx_document = self.portal[dx_document_id]
        migrate_simplefield(at_document, dx_document, 'subject', 'subject',)
        self.assertEqual(dx_document.Subject(), at_document.Subject())

    def test_migrate_imagefield(self):
        test_image_data = self.get_test_image_data()
        at_newsitem_id = self.portal.invokeFactory(
            'News Item',
            'foo',
            title="Foo news",
            image=test_image_data)
        # register p.a.contenttypes profile
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        dx_newsitem_id = self.portal.invokeFactory(
            'News Item',
            'bar',
            title="Bar news")
        at_newsitem = self.portal[at_newsitem_id]
        dx_newsitem = self.portal[dx_newsitem_id]
        self.assertEqual(dx_newsitem.image, None)
        migrate_imagefield(at_newsitem, dx_newsitem, 'image', 'image')
        self.assertEqual(dx_newsitem.image.contentType, 'image/png')
        self.assertEqual(dx_newsitem.image.data, test_image_data)

    def test_migrate_filefield(self):
        test_file_data = self.get_test_file_data()
        at_file_id = self.portal.invokeFactory('File',
                                               'foo',
                                               title="Foo file",
                                               file=test_file_data)
        # register p.a.contenttypes profile
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        dx_file_id = self.portal.invokeFactory('File',
                                               'bar',
                                               title="Bar file")
        at_file = self.portal[at_file_id]
        dx_file = self.portal[dx_file_id]
        self.assertEqual(dx_file.file, None)
        migrate_filefield(at_file, dx_file, 'file', 'file')
        self.assertEqual(dx_file.file.data, test_file_data)


class MigrateCustomATTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_MIGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def tearDown(self):
        try:
            applyProfile(self.portal, 'plone.app.contenttypes:uninstall')
        except KeyError:
            pass

    def createCustomATDocument(self, id, parent=None):
        from Products.Archetypes.atapi import StringField, TextField
        from Products.ATContentTypes.interface import IATDocument
        from archetypes.schemaextender.interfaces import ISchemaExtender
        from archetypes.schemaextender.field import ExtensionField
        from zope.component import getGlobalSiteManager
        from zope.interface import implements

        # create schema extension
        class ExtensionTextField(ExtensionField, TextField):
            """ derivative of text for extending schemas """

        class ExtensionStringField(ExtensionField, StringField):
            """ derivative of text for extending schemas """

        class SchemaExtender(object):
            implements(ISchemaExtender)
            fields = [
                ExtensionTextField('textExtended',
                                   ),
                ExtensionStringField('stringExtended',
                                     ),
            ]

            def __init__(self, context):
                self.context = context

            def getFields(self):
                return self.fields

        # register adapter
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(SchemaExtender, (IATDocument,), ISchemaExtender)

        # create content
        container = parent or self.portal
        container.invokeFactory('Document', id,
                                title="Foo document",
                                stringExtended="foo text",
                                textExtended='foo extended rich text')
        at_document = container[id]

        # unregister adapter assure test isolation
        gsm.unregisterAdapter(required=[IATDocument], provided=ISchemaExtender)

        return at_document

    def test_migrate_extended_document(self):
        from plone.app.contenttypes.migration.migration import migrateCustomAT
        from plone.app.contenttypes.interfaces import INewsItem
        at_document = self.createCustomATDocument('foo-document')
        qi = self.portal.portal_quickinstaller
        # install pac but only install News Items
        qi.installProduct(
            'plone.app.contenttypes',
            profile='plone.app.contenttypes:default',
            blacklistedSteps=['typeinfo'])
        installTypeIfNeeded("News Item")
        fields_mapping = (
            {'AT_field_name': 'textExtended',
             'AT_field_type': 'Products.Archetypes.Field.TextField',
             'DX_field_name': 'text',
             'DX_field_type': 'RichText', },
            {'AT_field_name': 'stringExtended',
             'AT_field_type': 'StringField',
             'DX_field_name': 'title',
             'DX_field_type': 'StringField', },
        )
        # migrate extended AT Document to default DX News Item
        migrateCustomAT(
            fields_mapping, src_type='Document', dst_type='News Item')
        dx_newsitem = self.portal['foo-document']
        self.assertTrue(INewsItem.providedBy(dx_newsitem))
        self.assertTrue(dx_newsitem is not at_document)
        self.assertEquals(at_document.textExtended(), dx_newsitem.text.raw)
        self.assertEquals(at_document.stringExtended, dx_newsitem.title)

    def test_migrate_atevent_to_dxnewsitem(self):
        """Tests the custom migration by migrating a default type. It is not
        meant to be used this way but is a nice way to test the migrations.
        During this migration the old event fti is still present.
        """
        from DateTime import DateTime
        from plone.app.contenttypes.migration.migration import migrateCustomAT
        from plone.app.contenttypes.interfaces import INewsItem

        # create an ATEvent
        self.portal.invokeFactory('Event', 'event')
        at_event = self.portal['event']

        # Date
        at_event.getField('startDate') \
                .set(at_event, DateTime('2013-02-03 12:00'))
        at_event.getField('endDate') \
                .set(at_event, DateTime('2013-04-05 13:00'))

        # Contact
        at_event.getField('contactPhone').set(at_event, '123456789')
        at_event.getField('contactEmail').set(at_event, 'dummy@email.com')
        at_event.getField('contactName').set(at_event, u'Näme')

        # URL
        at_event.getField('eventUrl').set(at_event, 'http://www.plone.org')

        # Attendees
        at_event.getField('attendees').set(at_event, ('You', 'Me'))

        # Text
        at_event.setText('Tütensuppe')
        at_event.setContentType('text/plain')

        oldTZ = os.environ.get('TZ', None)
        os.environ['TZ'] = 'Asia/Tbilisi'

        qi = self.portal.portal_quickinstaller
        # install pac but only install News Items
        qi.installProduct(
            'plone.app.contenttypes',
            profile='plone.app.contenttypes:default',
            blacklistedSteps=['typeinfo'])
        installTypeIfNeeded("News Item")
        fields_mapping = (
            {'AT_field_name': 'text',
             'AT_field_type': 'Products.Archetypes.Field.TextField',
             'DX_field_name': 'text',
             'DX_field_type': 'RichText', },
            {'AT_field_name': 'contactName',
             'AT_field_type': 'StringField',
             'DX_field_name': 'image_caption',
             'DX_field_type': 'StringField', },
        )
        # migrate ATCTEvent to default DX News Item
        migrateCustomAT(fields_mapping, src_type='Event', dst_type='News Item')
        dx_newsitem = self.portal['event']
        self.assertTrue(INewsItem.providedBy(dx_newsitem))
        self.assertTrue(dx_newsitem is not at_event)
        self.assertEquals(
            safe_unicode(at_event.getText()),
            dx_newsitem.text.output)
        self.assertEquals(
            at_event.contactName,
            dx_newsitem.image_caption)

    def test_migrate_atevent_to_dxevent(self):
        """Tests the custom migration by migrating a default type. It is not
        meant to be used this way but is a nice way to test the migrations.
        During this migration the event fti is already replaced by the dx one.
        """
        from DateTime import DateTime
        from plone.app.contenttypes.migration.migration import migrateCustomAT
        from plone.app.contenttypes.interfaces import IEvent

        # create an ATEvent
        self.portal.invokeFactory('Event', 'event')
        at_event = self.portal['event']

        # Date
        FORMAT = '%Y-%m-%d %H:%M'
        start = '2013-02-03 12:15'
        end = '2013-04-05 13:45'
        at_event.getField('startDate').set(at_event, DateTime(start))
        at_event.getField('endDate').set(at_event, DateTime(end))

        # Contact
        at_event.getField('contactPhone').set(at_event, '123456789')
        at_event.getField('contactEmail').set(at_event, 'dummy@email.com')
        at_event.getField('contactName').set(at_event, u'Näme')

        # URL
        at_event.getField('eventUrl').set(at_event, 'http://www.plone.org')

        # Attendees
        at_event.getField('attendees').set(at_event, ('Yöu', 'Me'))

        # Text
        at_event.setText('Tütensuppe')
        at_event.setContentType('text/plain')

        TZ = 'Asia/Tbilisi'
        os.environ['TZ'] = TZ
        timezone = pytz.timezone(TZ)

        qi = self.portal.portal_quickinstaller
        # install pac but only install Event
        qi.installProduct(
            'plone.app.contenttypes',
            profile='plone.app.contenttypes:default',
            blacklistedSteps=['typeinfo'])
        installTypeIfNeeded("Event")
        fields_mapping = (
            {'AT_field_name': 'startDate',
             'AT_field_type': 'Products.Archetypes.Field.DateTimeField',
             'DX_field_name': 'start',
             'DX_field_type': 'Datetime', },
            {'AT_field_name': 'endDate',
             'AT_field_type': 'Products.Archetypes.Field.DateTimeField',
             'DX_field_name': 'end',
             'DX_field_type': 'Datetime', },
            {'AT_field_name': 'text',
             'AT_field_type': 'Products.Archetypes.Field.TextField',
             'DX_field_name': 'text',
             'DX_field_type': 'RichText', },
            {'AT_field_name': 'eventUrl',
             'AT_field_type': 'Products.Archetypes.Field.StringField',
             'DX_field_name': 'event_url',
             'DX_field_type': 'StringField', },
            {'AT_field_name': 'contactEmail',
             'AT_field_type': 'Products.Archetypes.Field.StringField',
             'DX_field_name': 'contact_email',
             'DX_field_type': 'StringField', },
            {'AT_field_name': 'contactName',
             'AT_field_type': 'Products.Archetypes.Field.StringField',
             'DX_field_name': 'contact_name',
             'DX_field_type': 'StringField', },
            {'AT_field_name': 'contactPhone',
             'AT_field_type': 'Products.Archetypes.Field.StringField',
             'DX_field_name': 'contact_phone',
             'DX_field_type': 'StringField', },
            {'AT_field_name': 'attendees',
             'AT_field_type': 'Products.Archetypes.Field.LinesField',
             'DX_field_name': 'attendees',
             'DX_field_type': 'Tuple', },
        )
        # migrate ATEvent to new default Event
        migrateCustomAT(fields_mapping, src_type='Event', dst_type='Event')
        dx_event = self.portal['event']
        self.assertTrue(IEvent.providedBy(dx_event))
        self.assertTrue(dx_event is not at_event)
        self.assertEquals(safe_unicode(at_event.getText()), dx_event.text.output)
        self.assertEquals(at_event.eventUrl, dx_event.event_url)
        self.assertEquals(at_event.contactEmail, dx_event.contact_email)
        self.assertEquals(at_event.contactName, dx_event.contact_name)
        self.assertEquals(at_event.contactPhone, dx_event.contact_phone)
        self.assertEquals(at_event.attendees, dx_event.attendees)
        self.assertEquals(
            dx_event.start, timezone.localize(datetime.strptime(start, FORMAT)))
        self.assertEquals(
            dx_event.end, timezone.localize(datetime.strptime(end, FORMAT)))
