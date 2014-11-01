# -*- coding: utf-8 -*-
from plone.app.contenttypes.migration.migration import migrate_imagefield
from plone.app.contenttypes.migration.migration import migrate_simplefield
from plone.app.contenttypes.migration.utils import installTypeIfNeeded
from plone.app.contenttypes.testing import \
    PLONE_APP_CONTENTTYPES_MIGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import applyProfile
from plone.app.testing import setRoles

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
        at_newsitem_id = self.portal.invokeFactory('News Item',
                                                'foo',
                                                title="Foo news",
                                                image=test_image_data)
        # register p.a.contenttypes profile
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        dx_newsitem_id = self.portal.invokeFactory('News Item',
                                                'bar',
                                                title="Bar news")
        at_newsitem = self.portal[at_newsitem_id]
        dx_newsitem = self.portal[dx_newsitem_id]
        self.assertEqual(dx_newsitem.image, None)
        migrate_imagefield(at_newsitem, dx_newsitem, 'image', 'image')
        self.assertEqual(dx_newsitem.image.contentType, 'image/png')
        self.assertEqual(dx_newsitem.image.data, test_image_data)


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
        from plone.app.contenttypes.migration.migration import\
            migrateCustomAT
        from plone.app.contenttypes.interfaces import INewsItem
        at_document = self.createCustomATDocument('foo-document')
        qi = self.portal.portal_quickinstaller
        # install pac but only install News Items
        qi.installProduct(
            'plone.app.contenttypes',
            profile='plone.app.contenttypes:default',
            blacklistedSteps=['typeinfo'])
        installTypeIfNeeded("News Item")
        fields_mapping = ({'AT_field_name': 'textExtended',
                           'AT_field_type': 'TextField',
                           'DX_field_name': 'text',
                           'DX_field_type': 'TextField', },
                           {'AT_field_name': 'stringExtended',
                           'AT_field_type': 'StringField',
                           'DX_field_name': 'title',
                           'DX_field_type': 'StringField', },)
        # migrate extended AT Document to default DX News Item
        migrateCustomAT(fields_mapping, src_type='Document', dst_type='News Item')
        dx_newsitem = self.portal['foo-document']
        self.assertTrue(INewsItem.providedBy(dx_newsitem))
        self.assertTrue(dx_newsitem is not at_document)
        self.assertEquals(at_document.textExtended(), dx_newsitem.text.raw)
        self.assertEquals(at_document.stringExtended, dx_newsitem.title)
