# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from lxml import etree
from persistent.list import PersistentList
from plone.app.contenttypes.migration.migration import migrate_documents
from plone.app.contenttypes.migration.migration import migrate_folders
from plone.app.contenttypes.migration.migration import migrate_newsitems
from plone.app.contenttypes.migration.utils import add_portlet
from plone.app.contenttypes.migration.utils import installTypeIfNeeded
from plone.app.contenttypes.migration.utils import is_referenceable
from plone.app.contenttypes.migration.utils import restore_references
from plone.app.contenttypes.migration.utils import store_references
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING  # noqa
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_MIGRATION_FUNCTIONAL_TESTING  # noqa
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_MIGRATION_TESTING  # noqa
from plone.app.contenttypes.testing import set_browserlayer
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import applyProfile
from plone.app.testing import login
from plone.app.uuid.utils import uuidToObject
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.dexterity.content import Container
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityFTI
from plone.event.interfaces import IEventAccessor
from plone.namedfile.file import NamedBlobImage
from plone.testing.z2 import Browser
from z3c.relationfield import RelationValue
from z3c.relationfield.index import dump
from zc.relation.interfaces import ICatalog
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import alsoProvides
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import modified
from zope.schema.interfaces import IVocabularyFactory

import json
import os.path
import time
import transaction
import unittest2 as unittest


class MigrateFromATContentTypesTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_MIGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        self.request['URL'] = self.portal.absolute_url()
        self.catalog = getToolByName(self.portal, "portal_catalog")
        self.portal.acl_users.userFolderAddUser('admin',
                                                'secret',
                                                ['Manager'],
                                                [])
        login(self.portal, 'admin')
        self.portal.portal_workflow.setDefaultChain(
            "simple_publication_workflow")

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

    def get_migrator(self, obj, migrator_class):
        src_portal_type = migrator_class.src_portal_type
        dst_portal_type = migrator_class.dst_portal_type
        migrator = migrator_class(obj, src_portal_type=src_portal_type,
                                  dst_portal_type=dst_portal_type)
        return migrator

    def createATCTobject(self, klass, id, parent=None):
        '''Borrowed from ATCTFieldTestCase'''
        import transaction
        parent = parent if parent else self.portal
        obj = klass(oid=id)
        parent[id] = obj
        transaction.savepoint()
        # need to aq wrap after the savepoint. wrapped content can't be pickled
        obj = obj.__of__(parent)
        obj.initializeArchetype()
        return obj

    def createATCTBlobNewsItem(self, id, parent=None):
        from Products.Archetypes.atapi import StringField, TextField
        from Products.ATContentTypes.interface import IATNewsItem
        from archetypes.schemaextender.interfaces import ISchemaExtender
        from archetypes.schemaextender.field import ExtensionField
        from plone.app.blob.subtypes.image import ExtensionBlobField
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
                ExtensionTextField('text',
                                   primary=True,
                                   ),
                ExtensionBlobField('image',
                                   accessor='getImage',
                                   mutator='setImage',
                                   ),
                ExtensionStringField('imageCaption',
                                     ),
            ]

            def __init__(self, context):
                self.context = context

            def getFields(self):
                return self.fields

        # register adapter
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(SchemaExtender, (IATNewsItem,), ISchemaExtender)

        # create content
        container = parent or self.portal
        container.invokeFactory('News Item', id)
        at_newsitem = container['newsitem']

        # unregister adapter assure test isolation
        gsm.unregisterAdapter(required=[IATNewsItem], provided=ISchemaExtender)

        return at_newsitem

    def test_patct_event_is_migrated(self):
        """Can we migrate a Products.ATContentTypes event?"""
        from DateTime import DateTime
        from plone.app.contenttypes.migration.migration import migrate_events

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
        at_event.getField('contactName').set(at_event, 'Name')

        # URL
        at_event.getField('eventUrl').set(at_event, 'http://www.plone.org')

        # Attendees
        at_event.getField('attendees').set(at_event, ('You', 'Me'))

        # Text
        at_event.setText('Tütensuppe')
        at_event.setContentType('text/plain')

        oldTZ = os.environ.get('TZ', None)
        os.environ['TZ'] = 'Asia/Tbilisi'

        # migrate
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrate_events(self.portal)

        if oldTZ:
            os.environ['TZ'] = oldTZ
        else:
            del os.environ['TZ']

        # assertions
        dx_event = self.portal['event']
        self.assertEqual(
            "<class 'Products.ATContentTypes.content.event.ATEvent'>",
            str(at_event.__class__),
        )
        self.assertEqual(
            "<class 'plone.app.contenttypes.content.Event'>",
            str(dx_event.__class__),
        )
        self.assertEqual(2013, dx_event.start.year)
        self.assertEqual(02, dx_event.start.month)
        self.assertEqual(03, dx_event.start.day)
        self.assertEqual(12, dx_event.start.hour)
        self.assertEqual('Asia/Tbilisi', str(dx_event.start.tzinfo))
        self.assertEqual(2013, dx_event.end.year)
        self.assertEqual(04, dx_event.end.month)
        self.assertEqual(05, dx_event.end.day)
        self.assertEqual(13, dx_event.end.hour)
        self.assertEqual('Asia/Tbilisi', str(dx_event.end.tzinfo))
        self.assertEqual('123456789', dx_event.contact_phone)
        self.assertEqual('dummy@email.com', dx_event.contact_email)
        self.assertEqual('Name', dx_event.contact_name)
        self.assertEqual('http://www.plone.org', dx_event.event_url)
        self.assertEqual(('You', 'Me'), dx_event.attendees)
        self.assertEquals('Event', dx_event.__class__.__name__)
        self.assertEqual(u'<p>T\xfctensuppe</p>', dx_event.text.output)
        self.assertEqual(u'Tütensuppe', dx_event.text.raw)

    @unittest.skip("Skip this test, until old type is mocked")
    def test_pae_atevent_is_migrated(self):
        """Can we migrate a plone.app.event AT event?"""
        from DateTime import DateTime
        from plone.testing import z2
        from plone.app.testing import applyProfile
        from plone.app.contenttypes.migration.migration import migrate_events

        # Enable plone.app.event.at
        z2.installProduct(self.layer['app'], 'plone.app.event.at')
        applyProfile(self.portal, 'plone.app.event.at:default')

        self.portal.invokeFactory('Event', 'pae-at-event')
        old_event = self.portal['pae-at-event']

        # Date
        old_event.getField('startDate') \
                 .set(old_event, DateTime('2013-01-01 12:00'))
        old_event.getField('endDate') \
                 .set(old_event, DateTime('2013-02-01 13:00'))
        old_event.getField('wholeDay').set(old_event, False)
        old_event.getField('timezone').set(old_event, 'Asia/Tbilisi')

        # Contact
        old_event.getField('contactPhone').set(old_event, '123456789')
        old_event.getField('contactEmail').set(old_event, 'dummy@email.com')
        old_event.getField('contactName').set(old_event, 'Name')

        # URL
        old_event.getField('eventUrl').set(old_event, 'http://www.plone.org')

        # Attendees
        old_event.getField('attendees').set(old_event, ('You', 'Me'))

        # Text
        old_event.setText('Tütensuppe')
        old_event.setContentType('text/plain')

        # migrate
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrate_events(self.portal)

        # Compare new and old events
        new_event = self.portal['pae-at-event']
        self.assertEqual(
            "<class 'plone.app.event.at.content.ATEvent'>",
            str(old_event.__class__),
        )
        self.assertEqual(
            "<class 'plone.app.contenttypes.content.Event'>",
            str(new_event.__class__),
        )
        self.assertEqual('Event', new_event.portal_type)
        self.assertEqual(2013, new_event.start.year)
        self.assertEqual(01, new_event.start.month)
        self.assertEqual(01, new_event.start.day)
        self.assertEqual(12, new_event.start.hour)
        self.assertEqual('Asia/Tbilisi', str(new_event.start.tzinfo))
        self.assertEqual(2013, new_event.end.year)
        self.assertEqual(02, new_event.end.month)
        self.assertEqual(01, new_event.end.day)
        self.assertEqual(13, new_event.end.hour)
        self.assertEqual('Asia/Tbilisi', str(new_event.end.tzinfo))
        self.assertEqual(u'Name', new_event.contact_name)
        self.assertEqual(u'dummy@email.com', new_event.contact_email)
        self.assertEqual(u'123456789', new_event.contact_phone)
        self.assertEqual(u'http://www.plone.org', new_event.event_url)
        self.assertEqual(u'<p>T\xfctensuppe</p>', new_event.text.output)
        self.assertEqual(u'Tütensuppe', new_event.text.raw)

    @unittest.skip("Skip this test, until old type is mocked")
    def test_pae_dxevent_is_migrated(self):
        from datetime import datetime
        from plone.app.contenttypes.migration.migration import migrate_events
        from plone.app.textfield.value import RichTextValue

        # Enable plone.app.event.dx
        from plone.app.testing import applyProfile
        applyProfile(self.portal, 'plone.app.event:testing')

        old_event = self.portal[self.portal.invokeFactory(
            'plone.app.event.dx.event',
            'dx-event',
            start=datetime(2011, 11, 11, 11, 0),
            end=datetime(2011, 11, 11, 12, 0),
            timezone="Asia/Tbilisi",
            whole_day=False,
        )]
        old_event_acc = IEventAccessor(old_event)
        old_event_acc.contact_name = 'George'
        old_event_acc.contact_email = 'me@geor.ge'
        old_event_acc.contact_phone = '+99512345'
        old_event_acc.event_url = 'http://geor.ge/event'
        # We need to manually place the value of the "text" field into
        # annotation storage
        richtext = RichTextValue(
            raw='Woo, yeah',
            mimeType='text/plain',
            outputMimeType='text/x-html-safe'
        )
        ann = IAnnotations(old_event)
        ann['plone.app.event.dx.behaviors.IEventSummary.text'] = richtext

        # migrate
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrate_events(self.portal)

        # Compare new and old events
        new_event = self.portal['dx-event']
        self.assertEqual(False, old_event.exclude_from_nav)
        self.assertEqual('Event', new_event.portal_type)
        self.assertEqual(2011, new_event.start.year)
        self.assertEqual(11, new_event.start.month)
        self.assertEqual(11, new_event.start.day)
        self.assertEqual(11, new_event.start.hour)
        self.assertEqual('Asia/Tbilisi', str(new_event.start.tzinfo))
        self.assertEqual(2011, new_event.end.year)
        self.assertEqual(11, new_event.end.month)
        self.assertEqual(11, new_event.end.day)
        self.assertEqual(12, new_event.end.hour)
        self.assertEqual('Asia/Tbilisi', str(new_event.end.tzinfo))
        self.assertEqual(u'George', new_event.contact_name)
        self.assertEqual(u'me@geor.ge', new_event.contact_email)
        self.assertEqual(u'+99512345', new_event.contact_phone)
        self.assertEqual(u'http://geor.ge/event', new_event.event_url)
        self.assertEqual(u'<p>Woo, yeah</p>', new_event.text.output)
        self.assertEqual('Woo, yeah', new_event.text.raw)
        self.assertEqual(False, new_event.exclude_from_nav)

    def test_pact_1_0_dxevent_is_migrated(self):
        from datetime import datetime
        import pytz
        from plone.app.contenttypes.migration.migration import migrate_events
        from plone.app.textfield.value import RichTextValue
        from plone.app.contenttypes.tests.oldtypes import create1_0EventType

        # Create a 1.0 Event object
        timezone = pytz.timezone('Asia/Tbilisi')
        create1_0EventType(self.portal)
        old_event = self.portal[self.portal.invokeFactory(
            'Event',
            'dx-event',
            location='Newbraska',
            start_date=timezone.localize(datetime(2019, 04, 02, 15, 20)),
            end_date=timezone.localize(datetime(2019, 04, 02, 16, 20)),
            attendees='Me & You',
            event_url='http://woo.com',
            contact_name='Frank',
            contact_email='me@fra.nk',
            contact_phone='+4412345',
        )]
        old_event.text = RichTextValue(
            raw=u'Awesüme',
            mimeType='text/plain',
            outputMimeType='text/x-html-safe'
        )

        # migrate
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrate_events(self.portal)

        # Compare new and old events
        new_event = self.portal['dx-event']
        self.assertEqual(False, old_event.exclude_from_nav)
        self.assertEqual('Event', new_event.portal_type)
        self.assertEqual(2019, new_event.start.year)
        self.assertEqual(04, new_event.start.month)
        self.assertEqual(02, new_event.start.day)
        self.assertEqual(15, new_event.start.hour)
        self.assertEqual('Asia/Tbilisi', str(new_event.start.tzinfo))
        self.assertEqual(2019, new_event.end.year)
        self.assertEqual(04, new_event.end.month)
        self.assertEqual(02, new_event.end.day)
        self.assertEqual(16, new_event.end.hour)
        self.assertEqual('Asia/Tbilisi', str(new_event.end.tzinfo))
        self.assertEqual(u'Frank', new_event.contact_name)
        self.assertEqual(u'Newbraska', new_event.location)
        self.assertEqual(u'me@fra.nk', new_event.contact_email)
        self.assertEqual(u'+4412345', new_event.contact_phone)
        self.assertEqual(u'http://woo.com', new_event.event_url)
        self.assertEqual(u'<p>Awesüme</p>', new_event.text.output)
        self.assertEqual(u'Awesüme', new_event.text.raw)
        self.assertEqual(False, new_event.exclude_from_nav)

    def test_dx_excl_from_nav_is_migrated(self):
        from datetime import datetime
        from plone.app.contenttypes.migration.migration import DXEventMigrator

        # Enable plone.app.event.dx
        from plone.app.testing import applyProfile
        applyProfile(self.portal, 'plone.app.event:testing')

        old_event = self.portal[self.portal.invokeFactory(
            'plone.app.event.dx.event',
            'dx-event',
            start=datetime(2011, 11, 11, 11, 0),
            end=datetime(2011, 11, 11, 12, 0),
            timezone="GMT",
            whole_day=False,
            exclude_from_nav=True,
        )]

        # migrate
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(old_event, DXEventMigrator)
        migrator.migrate()

        new_event = self.portal['dx-event']
        self.assertEqual(True, old_event.exclude_from_nav)
        self.assertEqual(True, new_event.exclude_from_nav)

    def test_assert_at_contenttypes(self):
        from plone.app.contenttypes.interfaces import IDocument
        self.portal.invokeFactory('Document', 'document')
        at_document = self.portal['document']
        self.assertEqual('ATDocument', at_document.meta_type)
        self.assertFalse(IDocument.providedBy(at_document))

    def test_dx_content_is_indexed(self):
        from plone.app.contenttypes.migration.migration import DocumentMigrator
        from plone.app.contenttypes.interfaces import IDocument
        self.portal.invokeFactory('Document', 'document')
        at_document = self.portal['document']
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_document, DocumentMigrator)
        migrator.migrate()
        brains = self.catalog(object_provides=IDocument.__identifier__)
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getObject(), self.portal["document"])

    def test_old_content_is_removed(self):
        from plone.app.contenttypes.migration.migration import DocumentMigrator
        self.portal.invokeFactory('Document', 'document')
        at_document = self.portal['document']
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_document, DocumentMigrator)
        migrator.migrate()
        brains = self.catalog(portal_type='Document')
        self.assertEqual(len(brains), 1)

    def test_old_content_is_unindexed(self):
        from Products.ATContentTypes.interfaces import IATDocument
        from plone.app.contenttypes.migration.migration import DocumentMigrator
        self.portal.invokeFactory('Document', 'document')
        at_document = self.portal['document']
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_document, DocumentMigrator)
        brains = self.catalog(object_provides=IATDocument.__identifier__)
        self.assertEqual(len(brains), 1)
        migrator.migrate()
        brains = self.catalog(object_provides=IATDocument.__identifier__)
        self.assertEqual(len(brains), 0)

    def test_document_is_migrated(self):
        from plone.app.contenttypes.migration.migration import DocumentMigrator
        from plone.app.contenttypes.interfaces import IDocument
        self.portal.invokeFactory('Document', 'document')
        at_document = self.portal['document']
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_document, DocumentMigrator)
        migrator.migrate()
        dx_document = self.portal['document']
        self.assertTrue(IDocument.providedBy(dx_document))
        self.assertTrue(at_document is not dx_document)

    def test_collection_is_migrated(self):
        from plone.app.contenttypes.migration.migration import \
            migrate_collections
        from plone.app.contenttypes.behaviors.collection import \
            ICollection as ICollectionBehavior
        from plone.app.contenttypes.interfaces import ICollection
        self.portal.invokeFactory('Collection', 'collection')
        at_collection = self.portal['collection']
        at_collection.setText("<p>Whopee</p>")
        query = [{
            'i': 'Type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'Document',
        }]
        at_collection.setQuery(query)
        at_collection.setLayout('folder_summary_view')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrate_collections(self.portal)
        dx_collection = self.portal['collection']
        self.assertTrue(ICollection.providedBy(dx_collection))
        self.assertTrue(at_collection is not dx_collection)
        wrapped = ICollectionBehavior(dx_collection)
        self.assertEqual(wrapped.query, query)
        self.assertEqual(dx_collection.text.output, "<p>Whopee</p>")
        at_collection.setLayout('summary_view')

    def test_document_content_is_migrated(self):
        from plone.app.contenttypes.migration.migration import DocumentMigrator
        from plone.app.textfield.interfaces import IRichTextValue

        # create an ATDocument
        self.portal.invokeFactory('Document', 'document')
        at_document = self.portal['document']
        at_document.setText('Tütensuppe')
        at_document.setContentType('chemical/x-gaussian-checkpoint')

        # migrate
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_document, DocumentMigrator)
        migrator.migrate()

        # assertions
        dx_document = self.portal['document']
        self.assertTrue(IRichTextValue(dx_document.text))
        self.assertEqual(dx_document.text.raw, u'Tütensuppe')
        self.assertEqual(dx_document.text.mimeType,
                         'chemical/x-gaussian-checkpoint')
        self.assertEqual(dx_document.text.outputMimeType, 'text/x-html-safe')

    def test_document_excludefromnav_is_migrated(self):
        from plone.app.contenttypes.migration.migration import DocumentMigrator

        # create an ATDocument
        self.portal.invokeFactory('Document', 'document')
        at_document = self.portal['document']
        at_document.setExcludeFromNav(True)

        # migrate
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_document, DocumentMigrator)
        migrator.migrate()

        # assertions
        dx_document = self.portal['document']
        self.assertTrue(dx_document.exclude_from_nav)

    def test_file_is_migrated(self):
        from Products.ATContentTypes.content.file import ATFile
        from plone.app.contenttypes.migration.migration import FileMigrator
        from plone.app.contenttypes.interfaces import IFile
        at_file = self.createATCTobject(ATFile, 'file')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_file, FileMigrator)
        migrator.migrate()
        dx_file = self.portal['file']
        self.assertTrue(IFile.providedBy(dx_file))
        self.assertTrue(at_file is not dx_file)

    def test_file_content_is_migrated(self):
        from plone.app.contenttypes.migration.migration import FileMigrator
        from plone.namedfile.interfaces import INamedBlobFile
        from Products.ATContentTypes.content.file import ATFile
        at_file = self.createATCTobject(ATFile, 'file')
        field = at_file.getField('file')
        field.set(at_file, 'dummydata')
        field.setFilename(at_file, 'dummyfile.txt')
        field.setContentType(at_file, 'text/dummy')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_file, FileMigrator)
        migrator.migrate()
        dx_file = self.portal['file']
        self.assertTrue(INamedBlobFile.providedBy(dx_file.file))
        self.assertEqual(dx_file.file.filename, 'dummyfile.txt')
        self.assertEqual(dx_file.file.contentType, 'text/dummy')
        self.assertEqual(dx_file.file.data, 'dummydata')

    def test_image_is_migrated(self):
        from Products.ATContentTypes.content.image import ATImage
        from plone.app.contenttypes.migration.migration import ImageMigrator
        from plone.app.contenttypes.interfaces import IImage
        at_image = self.createATCTobject(ATImage, 'image')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_image, ImageMigrator)
        migrator.migrate()
        dx_image = self.portal['image']
        self.assertTrue(IImage.providedBy(dx_image))
        self.assertTrue(at_image is not dx_image)

    def test_empty_image_is_migrated(self):
        """
        This should not happened cause the image field is required,
        but this is a special case in AT's FileField.
        """
        from Products.ATContentTypes.content.image import ATImage
        from plone.app.contenttypes.migration.migration import ImageMigrator
        at_image = self.createATCTobject(ATImage, 'image')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_image, ImageMigrator)
        migrator.migrate()
        dx_image = self.portal['image']
        self.assertEqual(dx_image.image, None)

    def test_image_content_is_migrated(self):
        from plone.app.contenttypes.migration.migration import ImageMigrator
        from plone.namedfile.interfaces import INamedBlobImage
        from Products.ATContentTypes.content.image import ATImage
        at_image = self.createATCTobject(ATImage, 'image')
        test_image_data = self.get_test_image_data()
        field = at_image.getField('image')
        field.set(at_image, test_image_data)
        field.setFilename(at_image, 'testimage.png')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_image, ImageMigrator)
        migrator.migrate()
        dx_image = self.portal['image']
        self.assertTrue(INamedBlobImage.providedBy(dx_image.image))
        self.assertEqual(dx_image.image.filename, 'testimage.png')
        self.assertEqual(dx_image.image.contentType, 'image/png')
        self.assertEqual(dx_image.image.data, test_image_data)

    def test_blob_file_is_migrated(self):
        from plone.app.contenttypes.migration.migration import BlobFileMigrator
        from plone.app.contenttypes.interfaces import IFile
        self.portal.invokeFactory('File', 'file')
        at_file = self.portal['file']
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_file, BlobFileMigrator)
        migrator.migrate()
        dx_file = self.portal['file']
        self.assertTrue(IFile.providedBy(dx_file))
        self.assertTrue(at_file is not dx_file)

    def test_blob_file_content_is_migrated(self):
        from plone.app.contenttypes.migration.migration import BlobFileMigrator
        from plone.namedfile.interfaces import INamedBlobFile
        self.portal.invokeFactory('File', 'file')
        at_file = self.portal['file']
        at_file.setFile('dummydata',
                        mimetype="text/dummy",
                        filename='dummyfile.txt')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_file, BlobFileMigrator)
        migrator.migrate()
        dx_file = self.portal['file']
        self.assertTrue(INamedBlobFile.providedBy(dx_file.file))
        self.assertEqual(dx_file.file.filename, 'dummyfile.txt')
        self.assertEqual(dx_file.file.contentType, 'text/dummy')
        self.assertEqual(dx_file.file.data, 'dummydata')

    def test_blob_image_is_migrated(self):
        from plone.app.contenttypes.migration.migration import\
            BlobImageMigrator
        from plone.app.contenttypes.interfaces import IImage
        self.portal.invokeFactory('Image', 'image')
        at_image = self.portal['image']
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_image, BlobImageMigrator)
        migrator.migrate()
        dx_image = self.portal['image']
        self.assertTrue(IImage.providedBy(dx_image))
        self.assertTrue(at_image is not dx_image)

    def test_empty_blob_image_is_migrated(self):
        """
        This should not happened cause the image field is required,
        but this is a special case in AT's FileField.
        """
        from plone.app.contenttypes.migration.migration import\
            BlobImageMigrator
        self.portal.invokeFactory('Image', 'image')
        at_image = self.portal['image']
        migrator = self.get_migrator(at_image, BlobImageMigrator)
        migrator.migrate()
        dx_image = self.portal['image']
        self.assertEqual(dx_image.image.data, '')

    def test_blob_image_content_is_migrated(self):
        from plone.app.contenttypes.migration.migration import\
            BlobImageMigrator
        from plone.namedfile.interfaces import INamedBlobImage
        self.portal.invokeFactory('Image', 'image')
        at_image = self.portal['image']
        test_image_data = self.get_test_image_data()
        at_image.setImage(test_image_data, filename='testimage.png')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_image, BlobImageMigrator)
        migrator.migrate()
        dx_image = self.portal['image']
        self.assertTrue(INamedBlobImage.providedBy(dx_image.image))
        self.assertEqual(dx_image.image.filename, 'testimage.png')
        self.assertEqual(dx_image.image.contentType, 'image/png')
        self.assertEqual(dx_image.image.data, test_image_data)

    def test_link_is_migrated(self):
        from plone.app.contenttypes.migration.migration import LinkMigrator
        from plone.app.contenttypes.interfaces import ILink
        self.portal.invokeFactory('Link', 'link')
        at_link = self.portal['link']
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_link, LinkMigrator)
        migrator.migrate()
        dx_link = self.portal['link']
        self.assertTrue(ILink.providedBy(dx_link))
        self.assertTrue(dx_link is not at_link)

    def test_link_content_is_migrated(self):
        from plone.app.contenttypes.migration.migration import LinkMigrator
        from plone.app.contenttypes.interfaces import ILink
        self.portal.invokeFactory('Link', 'link')
        at_link = self.portal['link']
        field = at_link.getField('remoteUrl')
        field.set(at_link, 'http://plone.org')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_link, LinkMigrator)
        migrator.migrate()
        dx_link = self.portal['link']
        self.assertTrue(ILink.providedBy(dx_link.link))
        self.assertEqual(dx_link.link.remoteUrl, u'http://plone.org')

    def test_newsitem_is_migrated(self):
        from plone.app.contenttypes.migration.migration import NewsItemMigrator
        from plone.app.contenttypes.interfaces import INewsItem
        self.portal.invokeFactory('News Item', 'newsitem')
        at_newsitem = self.portal['newsitem']
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_newsitem, NewsItemMigrator)
        migrator.migrate()
        dx_newsitem = self.portal['newsitem']
        self.assertTrue(INewsItem.providedBy(dx_newsitem))
        self.assertTrue(at_newsitem is not dx_newsitem)

    def test_newsitem_content_is_migrated(self):
        from plone.app.contenttypes.migration.migration import NewsItemMigrator
        from plone.app.textfield.interfaces import IRichTextValue
        from plone.namedfile.interfaces import INamedBlobImage

        # create an ATNewsItem
        self.portal.invokeFactory('News Item', 'newsitem')
        at_newsitem = self.portal['newsitem']
        at_newsitem.setText('Tütensuppe')
        at_newsitem.setContentType('chemical/x-gaussian-checkpoint')
        at_newsitem.setImageCaption('Daniel Düsentrieb')
        test_image_data = self.get_test_image_data()
        image_field = at_newsitem.getField('image')
        image_field.set(at_newsitem, test_image_data)
        image_field.setFilename(at_newsitem, 'testimage.png')

        # migrate
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_newsitem, NewsItemMigrator)
        migrator.migrate()

        # assertions
        dx_newsitem = self.portal['newsitem']
        self.assertTrue(INamedBlobImage.providedBy(dx_newsitem.image))
        self.assertEqual(dx_newsitem.image.filename, 'testimage.png')
        self.assertEqual(dx_newsitem.image.contentType, 'image/png')
        self.assertEqual(dx_newsitem.image.data, test_image_data)

        self.assertEqual(dx_newsitem.image_caption, u'Daniel Düsentrieb')

        self.assertTrue(IRichTextValue(dx_newsitem.text))
        self.assertEqual(dx_newsitem.text.raw, u'Tütensuppe')
        self.assertEqual(dx_newsitem.text.mimeType,
                         'chemical/x-gaussian-checkpoint')
        self.assertEqual(dx_newsitem.text.outputMimeType, 'text/x-html-safe')

    def test_blob_newsitem_is_migrated(self):
        from plone.app.contenttypes.migration.migration import\
            BlobNewsItemMigrator
        from plone.app.contenttypes.interfaces import INewsItem
        at_newsitem = self.createATCTBlobNewsItem('newsitem')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_newsitem, BlobNewsItemMigrator)
        migrator.migrate()
        dx_newsitem = self.portal['newsitem']
        self.assertTrue(INewsItem.providedBy(dx_newsitem))
        self.assertTrue(at_newsitem is not dx_newsitem)

    def test_blob_newsitem_content_is_migrated(self):
        from plone.app.contenttypes.migration.migration import \
            BlobNewsItemMigrator
        from plone.app.textfield.interfaces import IRichTextValue
        from plone.namedfile.interfaces import INamedBlobImage

        # create a BlobATNewsItem
        at_newsitem = self.createATCTBlobNewsItem('newsitem')
        at_newsitem.setText('Tütensuppe')
        at_newsitem.setContentType('chemical/x-gaussian-checkpoint')
        test_image_data = self.get_test_image_data()
        namedblobimage = NamedBlobImage(
            data=test_image_data, filename=u'testimage.png')
        at_newsitem.image = namedblobimage
        at_newsitem.image_caption = u'Daniel Düsentrieb'

        # migrate
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_newsitem, BlobNewsItemMigrator)
        migrator.migrate()
        dx_newsitem = self.portal['newsitem']

        # assertions
        self.assertTrue(INamedBlobImage.providedBy(dx_newsitem.image))
        self.assertEqual(dx_newsitem.image.filename, 'testimage.png')
        self.assertEqual(dx_newsitem.image.contentType, 'image/png')
        self.assertEqual(dx_newsitem.image.data, test_image_data)

        # self.assertEqual(dx_newsitem.image_caption, u'Daniel Düsentrieb')

        self.assertTrue(IRichTextValue(dx_newsitem.text))
        self.assertEqual(dx_newsitem.text.raw, u'Tütensuppe')
        self.assertEqual(
            dx_newsitem.text.mimeType, 'chemical/x-gaussian-checkpoint')

    def test_modifield_date_is_unchanged(self):
        set_browserlayer(self.request)

        # create folders
        self.portal.invokeFactory('Folder', 'folder1')
        at_folder1 = self.portal['folder1']
        self.portal.invokeFactory('Folder', 'folder2')
        at_folder2 = self.portal['folder2']
        self.portal.invokeFactory('Folder', 'folder3')
        at_folder3 = self.portal['folder3']
        at_folder2.invokeFactory('Folder', 'folder4')
        at_folder4 = at_folder2['folder4']

        # create ATDocuments
        at_folder1.invokeFactory('Document', 'doc1')
        at_doc1 = at_folder1['doc1']
        at_folder2.invokeFactory('Document', 'doc2')
        at_doc2 = at_folder2['doc2']
        self.portal.invokeFactory('Document', 'doc3')
        at_doc3 = self.portal['doc3']
        at_folder2.invokeFactory('News Item', 'newsitem1')
        at_newsitem1 = at_folder2['newsitem1']
        at_folder4.invokeFactory('News Item', 'newsitem2')
        at_newsitem2 = at_folder4['newsitem2']

        # be 100% sure the migration-date is after the creation-date
        time.sleep(0.1)

        # relate them
        at_doc1.setRelatedItems([at_doc2])
        at_doc2.setRelatedItems([at_newsitem1, at_doc3, at_doc1])
        at_doc3.setRelatedItems(at_doc1)
        at_folder1.setRelatedItems([at_doc2])
        at_folder2.setRelatedItems([at_doc1])

        at_folder1_date = at_folder1.ModificationDate()
        at_folder2_date = at_folder2.ModificationDate()
        at_folder3_date = at_folder3.ModificationDate()
        at_folder4_date = at_folder4.ModificationDate()
        at_doc1_date = at_doc1.ModificationDate()
        at_doc2_date = at_doc2.ModificationDate()
        at_doc3_date = at_doc3.ModificationDate()
        at_newsitem1_date = at_newsitem1.ModificationDate()
        at_newsitem2_date = at_newsitem2.ModificationDate()

        # migrate content
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self._enable_referenceable_for('Document')
        self._enable_referenceable_for('News Item')
        self._enable_referenceable_for('Folder')

        # we use the migration-view instead of calling the migratons by hand
        # to make sure the patch for notifyModified is used.
        migration_view = getMultiAdapter(
            (self.portal, self.request),
            name=u'migrate_from_atct'
        )

        # We call migration twice to make sure documents are migrated first.
        # This would result in changed modification-dates on the folders
        # unless this is patched in the migration-view.
        migration_view(
            migrate=True,
            content_types=['Document'],
            migrate_schemaextended_content=True,
            migrate_references=True,
            from_form=False,
        )
        migration_view(
            migrate=True,
            content_types=['Folder'],
            migrate_schemaextended_content=True,
            migrate_references=True,
            from_form=False,
        )

        dx_folder1 = self.portal['folder1']
        dx_folder2 = self.portal['folder2']
        dx_folder3 = self.portal['folder3']
        dx_folder4 = dx_folder2['folder4']

        dx_doc1 = dx_folder1['doc1']
        dx_doc2 = dx_folder2['doc2']
        dx_doc3 = self.portal['doc3']

        self.assertTrue(at_folder1 is not dx_folder1)
        self.assertTrue(at_folder2 is not dx_folder2)

        # assert ModificationDates
        self.assertEqual(at_folder1_date, dx_folder1.ModificationDate())
        self.assertEqual(at_folder2_date, dx_folder2.ModificationDate())
        self.assertEqual(at_folder3_date, dx_folder3.ModificationDate())
        self.assertEqual(at_folder4_date, dx_folder4.ModificationDate())
        self.assertEqual(at_doc1_date, dx_doc1.ModificationDate())
        self.assertEqual(at_doc2_date, dx_doc2.ModificationDate())
        self.assertEqual(at_doc3_date, dx_doc3.ModificationDate())
        self.assertEqual(at_newsitem1_date, at_newsitem1.ModificationDate())
        self.assertEqual(at_newsitem2_date, at_newsitem2.ModificationDate())

        # assert single references
        dx_doc1_related = [x.to_object for x in dx_doc1.relatedItems]
        self.assertEqual(dx_doc1_related, [dx_doc2])

        dx_doc3_related = [x.to_object for x in dx_doc3.relatedItems]
        self.assertEqual(dx_doc3_related, [dx_doc1])

        dx_folder1_related = [x.to_object for x in dx_folder1.relatedItems]
        self.assertEqual(dx_folder1_related, [dx_doc2])
        dx_folder2_related = [x.to_object for x in dx_folder2.relatedItems]
        self.assertEqual(dx_folder2_related, [dx_doc1])

        # assert multi references, order is restored
        dx_doc2_related = [x.to_object for x in dx_doc2.relatedItems]
        self.assertEqual(dx_doc2_related, [at_newsitem1, dx_doc3, dx_doc1])

    def test_folder_is_migrated(self):
        from plone.app.contenttypes.migration.migration import FolderMigrator
        from plone.app.contenttypes.interfaces import IFolder
        self.portal.invokeFactory('Folder', 'folder')
        at_folder = self.portal['folder']
        at_folder.setLayout('atct_album_view')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_folder, FolderMigrator)
        migrator.migrate()
        dx_folder = self.portal['folder']
        self.assertTrue(IFolder.providedBy(dx_folder))
        self.assertTrue(at_folder is not dx_folder)
        self.assertEqual(dx_folder.getLayout(), 'album_view')

    def test_folder_children_are_migrated(self):
        from plone.app.contenttypes.migration.migration import FolderMigrator
        self.portal.invokeFactory('Folder', 'folder')
        at_folder = self.portal['folder']
        at_folder.invokeFactory('Document', 'document')
        at_child = at_folder['document']
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_folder, FolderMigrator)
        migrator.migrate()
        dx_folder = self.portal['folder']
        self.assertTrue(at_child in dx_folder.contentValues())

    def test_relations_are_migrated(self):
        # create folders
        self.portal.invokeFactory('Folder', 'folder1')
        at_folder1 = self.portal['folder1']
        self.portal.invokeFactory('Folder', 'folder2')
        at_folder2 = self.portal['folder2']

        # create ATDocuments
        at_folder1.invokeFactory('Document', 'doc1')
        at_doc1 = at_folder1['doc1']
        at_folder2.invokeFactory('Document', 'doc2')
        at_doc2 = at_folder2['doc2']
        self.portal.invokeFactory('Document', 'doc3')
        at_doc3 = self.portal['doc3']
        at_folder1.invokeFactory('News Item', 'newsitem')
        at_newsitem = at_folder1['newsitem']

        # relate them
        at_doc1.setRelatedItems([at_doc2])
        at_doc2.setRelatedItems([at_newsitem, at_doc3, at_doc1])
        at_doc3.setRelatedItems(at_doc1)
        at_folder1.setRelatedItems([at_doc2])
        at_folder2.setRelatedItems([at_doc1])
        self.assertEqual([x for x in at_folder2.getRelatedItems()], [at_doc1])
        # migrate content
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self._enable_referenceable_for('Folder')
        self._enable_referenceable_for('Document')
        self._enable_referenceable_for('News Item')
        store_references(self.portal)
        migrate_documents(self.portal)
        migrate_folders(self.portal)

        # rebuild catalog
        self.portal.portal_catalog.clearFindAndRebuild()

        dx_folder1 = self.portal['folder1']
        dx_folder2 = self.portal['folder2']

        dx_doc1 = dx_folder1['doc1']
        dx_doc2 = dx_folder2['doc2']
        dx_doc3 = self.portal['doc3']

        self.assertEqual([x.to_object for x in dx_folder2.relatedItems], [])

        # migrate references
        restore_references(self.portal)

        self.assertEqual(
            [x.to_object for x in dx_folder2.relatedItems], [dx_doc1])

        # assert single references
        dx_doc1_related = [x.to_object for x in dx_doc1.relatedItems]
        self.assertEqual(dx_doc1_related, [dx_doc2])

        dx_doc3_related = [x.to_object for x in dx_doc3.relatedItems]
        self.assertEqual(dx_doc3_related, [dx_doc1])

        dx_folder1_related = [x.to_object for x in dx_folder1.relatedItems]
        self.assertEqual(dx_folder1_related, [dx_doc2])
        dx_folder2_related = [x.to_object for x in dx_folder2.relatedItems]
        self.assertEqual(dx_folder2_related, [dx_doc1])

        # assert multi references, order is restored
        dx_doc2_related = [x.to_object for x in dx_doc2.relatedItems]
        self.assertEqual(dx_doc2_related, [at_newsitem, dx_doc3, dx_doc1])

    def test_backrelations_are_migrated_for_unnested_content(self):
        """relate a doc to a newsitem, migrate the newsitem but not the doc.
        check if the relations are still in place."""

        # create ATFolder and ATDocument
        self.portal.invokeFactory('News Item', 'news')
        at_news = self.portal['news']
        self.portal.invokeFactory('Document', 'doc')
        at_doc = self.portal['doc']

        # relate them
        at_news.setRelatedItems([at_doc])

        self.assertEqual(at_news.getRelatedItems(), [at_doc])
        self.assertEqual(at_news.getReferences(), [at_doc])
        self.assertEqual(at_news.getBackReferences(), [])
        self.assertEqual(at_doc.getReferences(), [])
        self.assertEqual(at_doc.getBackReferences(), [at_news])

        # migrate content (stores references on new objects for later restore)
        applyProfile(
            self.portal,
            'plone.app.contenttypes:default',
            # blacklisted_steps=['typeinfo']
        )
        # installTypeIfNeeded('News Item')
        store_references(self.portal)
        migrate_newsitems(self.portal)
        migrate_documents(self.portal)

        # rebuild catalog
        self.portal.portal_catalog.clearFindAndRebuild()

        dx_news = self.portal['news']
        dx_doc = self.portal['doc']

        # references are not restored yet
        self.assertEqual(dx_news.relatedItems, [])
        self.assertEqual(at_doc.getReferences(), [])
        self.assertEqual(at_doc.getBackReferences(), [])

        # restore references
        restore_references(self.portal)

        # references should be restored
        self.assertEqual([i.to_object for i in dx_news.relatedItems], [dx_doc])
        self.assertEqual([i.to_object for i in dx_doc.relatedItems], [])
        self.assertEqual(self._backrefs(dx_doc), [dx_news])
        self.assertEqual(self._backrefs(dx_news), [])

    def test_dx_at_relations_migrated_for_partially_migrated_nested(self):
        """This fails if referenceablebehavior is not enabled
        """
        # create ATFolder and ATDocument
        self.portal.invokeFactory('Folder', 'folder')
        at_folder = self.portal['folder']
        at_folder.invokeFactory('Document', 'doc')
        at_doc = at_folder['doc']

        # relate them
        at_folder.setRelatedItems([at_doc])

        self.assertEqual(at_folder.getRelatedItems(), [at_doc])
        self.assertEqual(at_folder.getReferences(), [at_doc])
        self.assertEqual(at_folder.getBackReferences(), [])
        self.assertEqual(at_doc.getReferences(), [])
        self.assertEqual(at_doc.getBackReferences(), [at_folder])

        # migrate content (stores references on new objects for later restore)
        applyProfile(
            self.portal,
            'plone.app.contenttypes:default',
            blacklisted_steps=['typeinfo'])
        installTypeIfNeeded('Folder')
        self._enable_referenceable_for('Folder')

        store_references(self.portal)
        migrate_folders(self.portal)

        # rebuild catalog
        self.portal.portal_catalog.clearFindAndRebuild()

        dx_folder = self.portal['folder']
        at_doc = dx_folder['doc']
        # references are not restored yet
        self.assertEqual(dx_folder.relatedItems, [])
        self.assertEqual(at_doc.getReferences(), [])
        self.assertEqual(at_doc.getBackReferences(), [])

        # restore references
        restore_references(self.portal)

        # references should be restored
        self.assertEqual(
            [i.to_object for i in dx_folder.relatedItems], [at_doc])
        self.assertEqual(self._backrefs(at_doc), [dx_folder])
        self.assertEqual(self._backrefs(dx_folder), [])
        self.assertEqual(at_doc.getReferences(), [])
        self.assertEqual(at_doc.getBackReferences(), [])

    def test_at_dx_relations_migrated_for_partialy_migrated_nested(self):
        """Fails if referenceablebehavior is not enabled"""
        # create ATFolder and ATDocument
        self.portal.invokeFactory('Folder', 'folder')
        at_folder = self.portal['folder']
        at_folder.invokeFactory('Document', 'doc')
        at_doc = at_folder['doc']

        # relate them
        at_folder.setRelatedItems([at_doc])

        self.assertEqual(at_folder.getRelatedItems(), [at_doc])
        self.assertEqual(at_folder.getReferences(), [at_doc])
        self.assertEqual(at_folder.getBackReferences(), [])
        self.assertEqual(at_doc.getReferences(), [])
        self.assertEqual(at_doc.getBackReferences(), [at_folder])

        # migrate content (stores references on new objects for later restore)
        applyProfile(
            self.portal,
            'plone.app.contenttypes:default',
            blacklisted_steps=['typeinfo'])
        installTypeIfNeeded('Document')
        store_references(self.portal)
        migrate_documents(self.portal)
        self._enable_referenceable_for('Document')

        # rebuild catalog
        self.portal.portal_catalog.clearFindAndRebuild()

        at_folder = self.portal['folder']
        dx_doc = at_folder['doc']
        self.assertTrue(is_referenceable(dx_doc))
        self.assertTrue(is_referenceable(at_folder))

        # references are not restored yet
        # the at-folder has a broken reference now
        # since at_doc is now <ATDocument at /plone/folder/doc_MIGRATION_>
        self.assertNotEqual(at_folder.getRelatedItems(), [at_doc])
        self.assertEqual(dx_doc.relatedItems, [])
        # the backref is found since the reference_catalog is not purged
        self.assertEqual(self._backrefs(dx_doc), [at_folder])

        # restore references
        restore_references(self.portal)

        # references should be restored
        self.assertEqual(at_folder.getRelatedItems(), [dx_doc])
        self.assertEqual(self._backrefs(dx_doc), [at_folder])
        self.assertEqual(dx_doc.relatedItems, [])

    def _backrefs(self, obj):
        from Products.Archetypes.interfaces.referenceable import IReferenceable
        results = []
        relation_catalog = queryUtility(ICatalog)
        reference_catalog = getToolByName(obj, 'reference_catalog')
        int_id = dump(obj, relation_catalog, {})
        if int_id:
            brels = relation_catalog.findRelations(dict(to_id=int_id))
            for brel in brels:
                if brel.isBroken():
                    results.append('broken')
                else:
                    results.append(brel.from_object)
        if not results:
            if is_referenceable(obj):
                obj = IReferenceable(obj)
                for rel in reference_catalog.getBackReferences(obj):
                    results.append(uuidToObject(rel.sourceUID))
        return results

    def _enable_referenceable_for(self, typename):
        behavior = 'plone.app.referenceablebehavior.referenceable.IReferenceable'  # noqa
        fti = queryUtility(IDexterityFTI, name=typename)
        behaviors = list(fti.behaviors)
        behaviors.append(behavior)
        fti._updateProperty('behaviors', tuple(behaviors))

    def test_store_references(self):
        intids = getUtility(IIntIds)

        applyProfile(
            self.portal,
            'plone.app.contenttypes:default',
            blacklisted_steps=['typeinfo'])
        installTypeIfNeeded('News Item')

        # create ATFolder and ATDocument
        self.portal.invokeFactory('Folder', 'folder')
        at_folder = self.portal['folder']
        self.portal.invokeFactory('Document', 'doc')
        at_doc = self.portal['doc']
        # relate them
        at_folder.setRelatedItems([at_doc])

        # create DX News Items
        self.portal.invokeFactory('News Item', 'news1')
        dx_news1 = self.portal['news1']
        self.portal.invokeFactory('News Item', 'news2')
        dx_news2 = self.portal['news2']
        dx_news1.relatedItems = PersistentList()
        dx_news1.relatedItems.append(RelationValue(intids.getId(dx_news2)))
        modified(dx_news1)
        relation_catalog = queryUtility(ICatalog)
        all_rels = [i for i in relation_catalog.findRelations()]
        self.assertEqual(len(all_rels), 1)

        self.assertEqual(at_folder.getRelatedItems(), [at_doc])
        self.assertEqual(at_folder.getReferences(), [at_doc])
        self.assertEqual(at_folder.getBackReferences(), [])
        self.assertEqual(at_doc.getReferences(), [])
        self.assertEqual(at_doc.getBackReferences(), [at_folder])
        self.assertEqual(
            [i.to_object for i in dx_news1.relatedItems], [dx_news2])

        store_references(self.portal)
        key = 'ALL_REFERENCES'
        self.assertEqual(len(IAnnotations(self.portal)[key]), 2)

    def test_export_references(self):
        """Test the Browser-View @@export_all_references."""
        intids = getUtility(IIntIds)
        set_browserlayer(self.request)

        applyProfile(
            self.portal,
            'plone.app.contenttypes:default',
            blacklisted_steps=['typeinfo'])
        installTypeIfNeeded('News Item')

        # create ATFolder and ATDocument
        self.portal.invokeFactory('Folder', 'folder')
        at_folder = self.portal['folder']
        self.portal.invokeFactory('Document', 'doc')
        at_doc = self.portal['doc']
        # relate them
        at_folder.setRelatedItems([at_doc])

        # create DX News Items
        self.portal.invokeFactory('News Item', 'news1')
        dx_news1 = self.portal['news1']
        self.portal.invokeFactory('News Item', 'news2')
        dx_news2 = self.portal['news2']

        # relate them
        dx_news1.relatedItems = PersistentList()
        dx_news1.relatedItems.append(RelationValue(intids.getId(dx_news2)))
        modified(dx_news1)

        view = self.portal.restrictedTraverse('export_all_references')
        result = view()
        data = json.loads(result)
        self.assertEqual(len(data), 2)

    def test_migrate_references_with_storage_on_portal(self):
        set_browserlayer(self.request)
        intids = getUtility(IIntIds)

        applyProfile(
            self.portal,
            'plone.app.contenttypes:default',
            blacklisted_steps=['typeinfo'])
        installTypeIfNeeded('News Item')
        self._enable_referenceable_for('News Item')

        # create ATFolder and ATDocument
        self.portal.invokeFactory('Folder', 'folder')
        at_folder = self.portal['folder']
        self.portal.invokeFactory('Document', 'doc')
        at_doc = self.portal['doc']

        # create DX News Items
        self.portal.invokeFactory('News Item', 'news1')
        dx_news1 = self.portal['news1']
        self.portal.invokeFactory('News Item', 'news2')
        dx_news2 = self.portal['news2']

        # relate them
        at_folder.setRelatedItems([at_doc])
        dx_news1.relatedItems = PersistentList()
        dx_news1.relatedItems.append(RelationValue(intids.getId(dx_news2)))
        dx_news1.relatedItems.append(RelationValue(intids.getId(at_doc)))
        at_doc.setRelatedItems([dx_news2])
        modified(dx_news1)
        relation_catalog = queryUtility(ICatalog)
        all_rels = [i for i in relation_catalog.findRelations()]
        self.assertEqual(len(all_rels), 2)

        store_references(self.portal)
        # migration_view = getMultiAdapter(
        #     (self.portal, self.request),
        #     name=u'migrate_from_atct'
        # )
        # migration_view(from_form=True, migrate_references=False)

        # this is basically be the same as above
        installTypeIfNeeded('Document')
        installTypeIfNeeded('Folder')
        migrate_folders(self.portal)
        migrate_documents(self.portal)
        self.portal.portal_catalog.clearFindAndRebuild()
        restore_references(self.portal)

        dx_folder = self.portal['folder']
        dx_doc = self.portal['doc']
        self.assertEqual(
            [i.to_object for i in dx_folder.relatedItems], [dx_doc])
        self.assertEqual(
            [i.to_object for i in dx_doc.relatedItems], [dx_news2])
        self.assertEqual(
            [i.to_object for i in dx_news1.relatedItems], [dx_news2, dx_doc])

    def test_stats(self):
        from plone.app.contenttypes.migration.migration import DocumentMigrator
        from plone.app.contenttypes.migration.browser import \
            MigrateFromATContentTypes as MigrationView

        self.portal.invokeFactory('Document', 'doc1')
        at_doc1 = self.portal['doc1']
        self.portal.invokeFactory('Document', 'doc2')
        at_doc2 = self.portal['doc2']
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrationview = MigrationView(self.portal, None)
        stats = migrationview.stats()
        self.assertEqual(str(stats), "{'ATDocument': 2}")
        migrator = self.get_migrator(at_doc1, DocumentMigrator)
        migrator.migrate()
        stats = migrationview.stats()
        self.assertEqual(str(stats), "{'Document': 1, 'ATDocument': 1}")
        migrator = self.get_migrator(at_doc2, DocumentMigrator)
        migrator.migrate()
        stats = migrationview.stats()
        self.assertEqual(str(stats), "{'Document': 2}")

    def test_migration_atctypes_vocabulary_registered(self):
        name = 'plone.app.contenttypes.migration.atctypes'
        factory = getUtility(IVocabularyFactory, name)
        self.assertIsNotNone(factory,
                             'Vocabulary %s does not exist' % name)

        vocabulary = factory(self.portal)
        self.assertEqual((), tuple(vocabulary))

    def test_migration_atctypes_vocabulary_result(self):
        from Products.ATContentTypes.content.document import ATDocument
        from Products.ATContentTypes.content.file import ATFile
        from Products.ATContentTypes.content.image import ATImage
        from Products.ATContentTypes.content.folder import ATFolder
        from Products.ATContentTypes.content.link import ATLink

        name = 'plone.app.contenttypes.migration.atctypes'
        factory = getUtility(IVocabularyFactory, name)

        self.createATCTobject(ATDocument, 'doc1')
        self.createATCTobject(ATDocument, 'doc2')
        self.createATCTobject(ATFile, 'file')
        self.createATCTobject(ATImage, 'image')
        self.createATCTobject(ATFolder, 'folder')
        self.createATCTobject(ATLink, 'link')

        vocabulary = factory(self.portal)

        self.assertEqual(
            5,
            len(vocabulary),
            'Expect 5 entries in vocab because there are 5 diffrent types')

        # Result format
        docs = [term for term in vocabulary if term.token == 'Document'][0]
        self.assertEqual('Document', docs.value)
        self.assertEqual('Document (2)', docs.title)

    def test_migration_extendedtypes_vocabulary_registered(self):
        name = 'plone.app.contenttypes.migration.extendedtypes'
        factory = getUtility(IVocabularyFactory, name)
        self.assertIsNotNone(factory,
                             'Vocabulary %s does not exist' % name)

        vocabulary = factory(self.portal)
        self.assertEqual((), tuple(vocabulary))

    @unittest.skip('Creates test-isolation-issues. See https://github.com/plone/plone.app.contenttypes/issues/251')  # noqa
    def test_migration_extendedtypes_vocabulary_result(self):
        from archetypes.schemaextender.extender import CACHE_ENABLED
        from archetypes.schemaextender.extender import CACHE_KEY
        from archetypes.schemaextender.field import ExtensionField
        from archetypes.schemaextender.interfaces import ISchemaExtender
        from Products.Archetypes import atapi
        from Products.ATContentTypes.content.document import ATDocument
        from zope.component import adapts
        from zope.component import provideAdapter
        from zope.interface import classImplements
        from zope.interface import implements
        from zope.interface import Interface

        name = 'plone.app.contenttypes.migration.extendedtypes'
        factory = getUtility(IVocabularyFactory, name)

        class IDummy(Interface):
            """Taggable content
            """

        classImplements(ATDocument, IDummy)
        doc = self.createATCTobject(ATDocument, 'doc')

        class DummyField(ExtensionField, atapi.StringField):
            """Dummy Field"""

        class DummySchemaExtender(object):
            implements(ISchemaExtender)
            adapts(IDummy)

            _fields = [DummyField('dummy')]

            def __init__(self, context):
                self.context = context

            def getFields(self):
                return self._fields

        provideAdapter(DummySchemaExtender, name=u"dummy.extender")

        # Clear cache
        if CACHE_ENABLED:
            delattr(self.request, CACHE_KEY)
        self.assertIn('dummy', doc.Schema()._names)

        vocabulary = factory(self.portal)

        self.assertEqual(1, len(vocabulary), 'Expect one entry')

        self.assertEqual("Document (1) - extended fields: 'dummy'",
                         tuple(vocabulary)[0].title)

    def test_migrate_function(self):
        from plone.app.contenttypes.migration.migration import migrate
        from plone.app.contenttypes.migration.migration import DocumentMigrator
        self.portal.invokeFactory('Document', 'document')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrate(self.portal, DocumentMigrator)
        dx_document = self.portal["document"]
        self.assertTrue(IDexterityContent.providedBy(dx_document))

    def test_migrate_xx_functions(self):
        from Products.ATContentTypes.content.image import ATImage
        from Products.ATContentTypes.content.file import ATFile
        from plone.app.contenttypes.migration.migration import (
            migrate_documents,
            migrate_collections,
            migrate_images,
            migrate_blobimages,
            migrate_files,
            migrate_blobfiles,
            migrate_links,
            migrate_newsitems,
            migrate_blobnewsitems,
            migrate_folders,
            migrate_events,
        )
        from plone.app.contenttypes.migration.topics import migrate_topics

        # create all content types
        self.portal.invokeFactory('Document', 'document')
        self.portal.invokeFactory('Image', 'image')
        self.createATCTobject(ATImage, 'blobimage')
        self.portal.invokeFactory('File', 'blobfile')
        self.createATCTobject(ATFile, 'file')
        self.portal.invokeFactory('Collection', 'collection')
        self.portal.invokeFactory('Link', 'link')
        self.portal.invokeFactory('News Item', 'newsitem')
        self.createATCTBlobNewsItem('blobnewsitem')
        self.portal.invokeFactory('Folder', 'folder')
        self.portal.invokeFactory('Event', 'event')
        self.portal.invokeFactory('Topic', 'topic')

        # migrate all
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrate_documents(self.portal)
        migrate_collections(self.portal)
        migrate_images(self.portal)
        migrate_blobimages(self.portal)
        migrate_files(self.portal)
        migrate_blobfiles(self.portal)
        migrate_links(self.portal)
        migrate_newsitems(self.portal)
        migrate_blobnewsitems(self.portal)
        migrate_folders(self.portal)
        migrate_events(self.portal)
        migrate_topics(self.portal)

        # assertions
        cat = self.catalog
        at_contents = cat(object_provides='Products.ATContentTypes'
                          '.interfaces.IATContentType')
        dx_contents = cat(object_provides='plone.dexterity'
                          '.interfaces.IDexterityContent')
        self.assertEqual(len(at_contents), 0)
        self.assertEqual(len(dx_contents), 12)

    def test_warning_for_uneditable_content(self):
        set_browserlayer(self.request)
        from plone.app.contenttypes.migration.migration import DocumentMigrator
        from plone.app.contenttypes.interfaces import IDocument
        self.portal.invokeFactory('Document', 'document')
        self.portal.invokeFactory('News Item', 'newsitem')
        at_document = self.portal['document']
        at_newsitem = self.portal['newsitem']
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        # At this point plone.app.z3cform is installed including it's browser
        # layer. But we have to annotate the request to provide it, since the
        # request was constructed before. Otherwise, @@view cannot be render
        # it's IRichText widget.
        alsoProvides(self.request, IPloneFormLayer)
        at_document_view = at_document.restrictedTraverse('')
        self.assertTrue(
            'http://nohost/plone/@@atct_migrator' in at_document_view()
        )
        migrator = self.get_migrator(at_document, DocumentMigrator)
        migrator.migrate()
        dx_document = self.portal['document']
        self.assertTrue(IDocument.providedBy(dx_document))
        dx_document_view = dx_document.restrictedTraverse('@@view')
        self.assertFalse('alert-box' in dx_document_view())
        at_newsitem_view = at_newsitem.restrictedTraverse('')
        self.assertTrue('alert-box' in at_newsitem_view())
        self.assertTrue(
            'http://nohost/plone/@@atct_migrator' in at_newsitem_view()
        )

    def test_aaa_migration_results_page(self):
        """We create dx-types with the same portal_type as other contenttypes
        before migration to make sure the stats are correct.
        """
        set_browserlayer(self.request)
        from plone.app.contenttypes.interfaces import IDocument
        from plone.app.contenttypes.interfaces import ICollection

        # create folders
        self.portal.invokeFactory('Folder', 'folder1')
        at_folder1 = self.portal['folder1']
        self.portal.invokeFactory('Folder', 'folder2')
        at_folder2 = self.portal['folder2']

        # create ATDocuments
        at_folder1.invokeFactory('Document', 'doc1')
        at_doc1 = at_folder1['doc1']
        at_folder2.invokeFactory('Document', 'doc2')
        at_doc2 = at_folder2['doc2']

        # create AT-based collections
        self.portal.invokeFactory('Collection', 'col1')
        at_col1 = self.portal['col1']

        # migrate content
        applyProfile(self.portal, 'plone.app.contenttypes:default')

        # create dx-content that will not be migrated
        at_folder1.invokeFactory('Document', 'dx_doc')
        dx_doc = at_folder1['dx_doc']
        self.assertTrue(IDocument.providedBy(dx_doc))

        # create dexterity-based collections
        self.portal.invokeFactory('Collection', 'dx_col')
        dx_col = self.portal['dx_col']
        self.assertTrue(ICollection.providedBy(dx_col))

        migration_view = getMultiAdapter(
            (self.portal, self.request),
            name=u'migrate_from_atct'
        )

        results = migration_view(
            from_form=True,
        )

        dx_folder1 = self.portal['folder1']
        dx_folder2 = self.portal['folder2']
        dx_doc1 = dx_folder1['doc1']
        dx_doc2 = dx_folder2['doc2']
        dx_col1 = self.portal['col1']

        self.assertTrue(at_folder1 is not dx_folder1)
        self.assertTrue(at_folder2 is not dx_folder2)
        self.assertTrue(at_doc1 is not dx_doc1)
        self.assertTrue(at_doc2 is not dx_doc2)
        self.assertTrue(at_col1 is not dx_col1)

        # test the stats
        stats = results['migrated_types']
        self.assertEqual(stats['Document']['amount_migrated'], 2)
        self.assertEqual(stats['Folder']['amount_migrated'], 2)
        self.assertEqual(stats['Collection']['amount_migrated'], 1)

    def test_migration_view_confirmation(self):
        set_browserlayer(self.request)
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migration_view = getMultiAdapter(
            (self.portal, self.request),
            name=u'migrate_from_atct'
        )
        results = migration_view()
        self.assertIn('@@migrate_from_atct?migrate=1', results)

    def test_portlets_are_migrated(self):
        """add portlets and see if they're still available on the migrated
        content including portlet settings.
        """
        from plone.app.contenttypes.migration.migration import DocumentMigrator
        from plone.app.contenttypes.migration.migration import FolderMigrator
        from plone.portlet.static.static import Assignment as StaticAssignment
        from plone.portlets.constants import GROUP_CATEGORY
        from plone.portlets.interfaces import ILocalPortletAssignmentManager
        from plone.portlets.interfaces import IPortletAssignmentMapping
        from plone.portlets.interfaces import IPortletAssignmentSettings
        from plone.portlets.interfaces import IPortletManager

        def get_portlets(context, columnName):
            column = getUtility(IPortletManager, columnName)
            mapping = getMultiAdapter((context, column),
                                      IPortletAssignmentMapping)
            return mapping

        # create an ATDocument
        self.portal.invokeFactory('Document', 'document')
        at_document = self.portal['document']
        at_document.setText(u'Tütensuppe with some portlet')
        at_document.setContentType('chemical/x-gaussian-checkpoint')

        # add a portlet
        portlet = StaticAssignment(u"Sample Portlet",
                                   "<p>Yay! I get migrated!</p>")
        add_portlet(at_document, portlet, 'static-portlet',
                    u'plone.leftcolumn')

        # disable group portlets for right columns
        right_column = getUtility(IPortletManager, u'plone.rightcolumn')
        localsettings = getMultiAdapter((at_document, right_column),
                                        ILocalPortletAssignmentManager)
        localsettings.setBlacklistStatus(GROUP_CATEGORY, True)

        # hide our portlet
        settings = IPortletAssignmentSettings(portlet)
        settings['visible'] = False

        # add another portlet type that is not available when doing the
        # migration and make sure it got ignored in the migration
        broken = StaticAssignment(u"Fake broken portlet",
                                  "<p>Ouch! I'm broken</p>")
        # ZODB.broken will add an ___Broken_state__ attribute if a portlet's
        # module is no longer available
        broken.__Broken_state__ = True
        add_portlet(at_document, broken, 'broken-portlet', u'plone.leftcolumn')

        # add a folder
        self.portal.invokeFactory('Folder', 'folder')
        at_folder = self.portal['folder']

        # add a portlet to the folder
        portlet2 = StaticAssignment(u"Sample Folder Portlet",
                                    "<p>Do I get migrated?</p>")
        add_portlet(at_folder, portlet2, 'static-portlet',
                    u'plone.rightcolumn')

        # migrate
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_document, DocumentMigrator)
        migrator.migrate()
        folder_migrator = self.get_migrator(at_folder, FolderMigrator)
        folder_migrator.migrate()

        # assertions
        dx_document = self.portal['document']

        # portlet is available
        self.failUnless('static-portlet' in get_portlets(dx_document,
                                                         u'plone.leftcolumn'))
        # broken portlets don't get copied
        self.failIf('broken-portlet' in get_portlets(dx_document,
                                                     u'plone.leftcolumn'))

        # block portlets settings copied
        right_column = getUtility(IPortletManager, u'plone.rightcolumn')
        localsettings = getMultiAdapter((dx_document, right_column),
                                        ILocalPortletAssignmentManager)
        self.assertTrue(localsettings.getBlacklistStatus(GROUP_CATEGORY))

        # hide portlets settings survived
        assignment = get_portlets(dx_document,
                                  u'plone.leftcolumn')['static-portlet']
        settings = IPortletAssignmentSettings(assignment)
        self.assertFalse(settings['visible'])

        dx_folder = self.portal['folder']
        self.failUnless('static-portlet' in get_portlets(dx_folder,
                                                         u'plone.rightcolumn'))

    def test_comments_are_migrated(self):
        """add some comments and check that it is correctly migrated.

        XXX fixme : original comment id is not kept, comments are created
        with new ids...
        """
        from zope.component import createObject
        from plone.app.discussion.interfaces import IConversation
        from plone.app.contenttypes.migration.migration import DocumentMigrator

        # create an ATDocument
        self.portal.invokeFactory('Document', 'document')
        at_document = self.portal['document']
        at_document.setText(u'Document with some comments')

        # add some comments to the document
        at_conversation = IConversation(at_document)
        new_comment = createObject('plone.Comment')
        new_comment.text = u"Hey Dude! Ä is not ascii."
        at_conversation.addComment(new_comment)
        at_comments = at_conversation.getComments()
        at_comment = [i for i in at_comments][0]
        at_plone_uuid = getattr(at_comment, '_plone.uuid')
        at_comment_id = getattr(at_comment, 'comment_id')

        # migrate
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_document, DocumentMigrator)
        migrator.migrate()

        dx_document = self.portal['document']

        # no more comments on the portal
        portal_conversation = IConversation(self.portal)
        self.failIf(portal_conversation)
        # comments were migrated
        dx_conversation = IConversation(dx_document)
        self.failUnless(len(dx_conversation) == 1)
        dx_comments = dx_conversation.getComments()
        dx_comment = [i for i in dx_comments][0]
        dx_comment_id = getattr(dx_comment, 'comment_id')
        self.assertEqual(dx_comment_id, at_comment_id)
        dx_plone_uuid = getattr(dx_comment, '_plone.uuid')
        self.assertEqual(dx_plone_uuid, at_plone_uuid)
        self.assertEqual(
            dx_comment.getText(),
            '<p>Hey Dude! \xc3\x84 is not ascii.</p>')

    def test_default_pages_are_kept_during_migration(self):
        """Check that the default pages are not lost when migrating."""
        set_browserlayer(self.request)
        # create some content and set default pages
        self.portal.invokeFactory('Document', 'document')
        at_document = self.portal['document']
        at_document.setText(u'Document with some comments')

        self.portal.invokeFactory('Folder', 'folder')
        at_folder = self.portal['folder']

        at_folder.invokeFactory('Document', 'subdocument')

        self.portal.setLayout('folder_summary_view')
        self.portal.setDefaultPage('document')

        at_folder.setLayout('folder_tabular_view')
        at_folder.setDefaultPage('subdocument')

        self.portal.invokeFactory('Folder', 'folder2')
        at_folder2 = self.portal['folder2']
        at_folder2.invokeFactory('Document', 'subdocument2')
        at_folder2.setLayout('folder_listing')

        # migrate content
        applyProfile(self.portal, 'plone.app.contenttypes:default')

        migration_view = getMultiAdapter(
            (self.portal, self.request),
            name=u'migrate_from_atct'
        )
        migration_view(from_form=True)
        dx_folder = self.portal['folder']
        dx_folder2 = self.portal['folder2']

        # test that view-methods are updated
        self.assertTrue(self.portal.getLayout(), 'summary_view')
        self.assertTrue(dx_folder.getLayout(), 'tabular_view')
        self.assertTrue(dx_folder2.getLayout(), 'listing_view')
        # test that defaultpage is kept
        self.assertTrue(self.portal.getDefaultPage(), 'document')
        self.assertTrue(dx_folder.getDefaultPage(), 'subdocument')
        self.assertIsNone(dx_folder2.getDefaultPage())


class MigrateDexterityBaseClassIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_MIGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        applyProfile(self.portal, 'plone.app.dexterity:testing')

        self.portal.acl_users.userFolderAddUser('admin',
                                                'secret',
                                                ['Manager'],
                                                [])
        login(self.portal, 'admin')

        # Add default content
        self.portal.invokeFactory('Document', 'item')

        # Change Document conent type to folderish
        portal_types = getToolByName(self.portal, 'portal_types')
        portal_types['Document'].klass = 'plone.dexterity.content.Container'
        portal_types['Document'].allowed_content_types = ('Document',)

    def test_dxmigration_migrate_item_to_container_class_is_changed(self):
        """Check that base class was changed."""
        from plone.app.contenttypes.migration.dxmigration import \
            migrate_base_class_to_new_class
        migrate_base_class_to_new_class(self.portal.item)
        self.assertTrue(isinstance(self.portal.item, Container))

    def test_dxmigration_migrate_item_to_container_add_object_inside(self):
        """Check that after migrate base class it can add items inside object.
        """
        from plone.app.contenttypes.migration.dxmigration import \
            migrate_base_class_to_new_class
        migrate_base_class_to_new_class(self.portal.item)
        self.portal.item.invokeFactory('Document', 'doc')
        self.assertEqual(
            len(self.portal.item.folderlistingFolderContents()), 1)

    def test_dxmigration_migrate_list_of_objects_with_changed_base_class(self):
        """Check list of objects with changed classes."""
        from plone.app.contenttypes.migration.dxmigration import \
            list_of_objects_with_changed_base_class
        # We have already one changed object
        objects = [i for i in
                   list_of_objects_with_changed_base_class(self.portal)]
        self.assertEqual(len(objects), 1)

    def test_dxmigration_migrate_list_of_changed_base_class_names(self):
        """Check list of changed base class names."""
        from plone.app.contenttypes.migration.dxmigration import \
            list_of_changed_base_class_names
        # We have already one changed object
        names = [i for i in list_of_changed_base_class_names(self.portal)]
        self.assertEqual(len(names), 1)

    def test_dxmigration_migrate_vocabulary_changed_base_classes(self):
        """Check vocabulary of changed base class names."""
        # We have already one changed object
        name = 'plone.app.contenttypes.migration.changed_base_classes'
        factory = getUtility(IVocabularyFactory, name)
        vocabulary = factory(self.portal)
        self.assertEqual(len(vocabulary), 1)


class MigrateDexterityBaseClassFunctionalTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        self.portal_url = self.portal.absolute_url()
        self.manage_document_url = '{0}/{1}/{2}/{3}'.format(
            self.portal_url,
            'portal_types',
            'Document',
            'manage_propertiesForm',
        )

        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

        # Add default content
        self.browser.open(self.portal_url)
        self.browser.getLink('Page').click()
        self.browser.getControl(name='form.widgets.IDublinCore.title')\
            .value = "My item"
        self.browser.getControl(name='form.widgets.IShortName.id')\
            .value = "item"
        self.browser.getControl('Save').click()

        # Change Document conent type to folderish
        self.browser.open(self.manage_document_url)
        self.browser.getControl(name='klass:string') \
            .value = 'plone.app.contenttypes.content.Collection'
        self.browser.getControl('Save Changes').click()
        self.browser.open(
            '{0}/@@base_class_migrator_form'.format(self.portal_url))
        self.good_info_message_template = 'There are {0} objects migrated.'

    def test_dxmigration_migrate_check_migration_form_view(self):
        """Check base class migrator view of changed base class names."""
        html = etree.HTML(self.browser.contents)
        checkboxes = html.xpath('//form//*[@name="{0}"]'.format(
            'form.widgets.changed_base_classes:list'))
        self.assertEqual(len(checkboxes), 1)

    def test_dxmigration_migrate_check_migration_successful_message(self):
        """Check base class migrator view of changed base class names."""
        self.browser.getControl(
            name='form.widgets.changed_base_classes:list').value = ['true']
        self.browser.getControl('Update').click()
        self.assertIn(
            self.good_info_message_template.format(1), self.browser.contents)


class MigrationFunctionalTests(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_MIGRATION_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        self.request['URL'] = self.portal.absolute_url()
        self.catalog = getToolByName(self.portal, "portal_catalog")
        self.portal.acl_users.userFolderAddUser('admin',
                                                'secret',
                                                ['Manager'],
                                                [])
        login(self.portal, 'admin')
        self.portal.portal_workflow.setDefaultChain(
            "simple_publication_workflow")
        self.portal_url = self.portal.absolute_url()

        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def tearDown(self):
        try:
            applyProfile(self.portal, 'plone.app.contenttypes:uninstall')
        except KeyError:
            pass

    def test_pac_installer_cancel(self):
        qi = self.portal.portal_quickinstaller
        portal_types = self.portal.portal_types
        self.browser.open('%s/@@pac_installer' % self.portal_url)
        self.assertFalse(qi.isProductInstalled('plone.app.contenttypes'))
        self.browser.getControl('Cancel').click()
        self.assertFalse(IDexterityFTI.providedBy(portal_types['Document']))
        self.assertFalse(qi.isProductInstalled('plone.app.contenttypes'))
        self.assertEqual(self.browser.url, self.portal_url)

    def test_pac_installer_without_content(self):
        qi = self.portal.portal_quickinstaller
        portal_types = self.portal.portal_types
        self.browser.open('%s/@@pac_installer' % self.portal_url)
        self.assertFalse(qi.isProductInstalled('plone.app.contenttypes'))
        self.assertFalse(IDexterityFTI.providedBy(portal_types['Document']))
        self.assertIn('proceed to the migration-form?', self.browser.contents)
        self.browser.getControl('Install').click()
        self.assertTrue(IDexterityFTI.providedBy(portal_types['Document']))
        self.assertTrue(IDexterityFTI.providedBy(portal_types['News Item']))
        self.assertTrue(qi.isProductInstalled('plone.app.contenttypes'))
        self.assertIn('Migration control panel', self.browser.contents)
        self.assertIn('No content to migrate.', self.browser.contents)

    def test_pac_installer_with_content(self):
        # add some at content:
        self.portal.invokeFactory('Document', 'doc1')
        transaction.commit()
        qi = self.portal.portal_quickinstaller
        portal_types = self.portal.portal_types
        self.browser.open('%s/@@pac_installer' % self.portal_url)
        self.assertFalse(IDexterityFTI.providedBy(portal_types['Document']))
        self.assertFalse(qi.isProductInstalled('plone.app.contenttypes'))
        self.assertIn('proceed to the migration-form?', self.browser.contents)
        self.browser.getControl('Install').click()
        self.assertFalse(IDexterityFTI.providedBy(portal_types['Document']))
        self.assertTrue(IDexterityFTI.providedBy(portal_types['News Item']))
        self.assertTrue(qi.isProductInstalled('plone.app.contenttypes'))
        self.assertIn('Migration control panel', self.browser.contents)
        self.assertIn('You currently have <span class="strong">1</span> archetypes objects to be migrated.', self.browser.contents)  # noqa

    def test_atct_migration_form(self):
        # setup session
        # taken from Products.Sessions.tests.testSessionDataManager._populate
        tf_name = 'temp_folder'
        idmgr_name = 'browser_id_manager'
        toc_name = 'temp_transient_container'
        sdm_name = 'session_data_manager'
        from Products.Sessions.BrowserIdManager import BrowserIdManager
        from Products.Sessions.SessionDataManager import SessionDataManager
        from Products.TemporaryFolder.TemporaryFolder import MountedTemporaryFolder  # noqa
        from Products.Transience.Transience import TransientObjectContainer
        bidmgr = BrowserIdManager(idmgr_name)
        tf = MountedTemporaryFolder(tf_name, title="Temporary Folder")
        toc = TransientObjectContainer(
            toc_name,
            title='Temporary Transient Object Container',
            timeout_mins=20)
        session_data_manager = SessionDataManager(
            id=sdm_name,
            path=tf_name+'/'+toc_name,
            title='Session Data Manager',
            requestName='TESTOFSESSION')
        self.portal._setObject(idmgr_name, bidmgr)
        self.portal._setObject(sdm_name, session_data_manager)
        self.portal._setObject(tf_name, tf)
        transaction.commit()
        self.portal.temp_folder._setObject(toc_name, toc)

        # add some at content:
        self.portal.invokeFactory('Document', 'doc1')
        transaction.commit()
        from zExceptions import NotFound
        self.assertRaises(NotFound, self.browser.open, '%s/@@atct_migrator' % self.portal_url)  # noqa
        self.browser.open('%s/@@pac_installer' % self.portal_url)
        self.browser.getControl('Install').click()
        self.assertIn('You currently have <span class="strong">1</span> archetypes objects to be migrated.', self.browser.contents)  # noqa

        self.browser.getControl(name='form.widgets.content_types:list').value = ['Document']  # noqa
        self.assertEqual(self.browser.getControl(name='form.widgets.migrate_references:list').value, ['selected'])  # noqa
        self.browser.getControl(name='form.buttons.migrate').click()
        self.assertIn('Congratulations! You migrated from Archetypes to Dexterity.', self.browser.contents)  # noqa
        msg = "<td>ATDocument</td>\n      <td>Document</td>\n      <td>1</td>"
        self.assertIn(msg, self.browser.contents)
