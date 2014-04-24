# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from five.intid.intid import IntIds
from five.intid.site import addUtility
from plone.app.contenttypes.testing import \
    PLONE_APP_CONTENTTYPES_MIGRATION_TESTING
from plone.app.contenttypes.testing import set_browserlayer
from plone.app.testing import applyProfile
from plone.app.testing import login
from plone.event.interfaces import IEventAccessor
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from zope.component import getSiteManager
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.schema.interfaces import IVocabularyFactory
import os.path
import time
import unittest2 as unittest
from plone.app.testing import TEST_USER_ID, setRoles
from test_image import dummy_image
from plone.app.contenttypes.migration.migration import migrate_imagefield, migrate_simplefield
from plone.app.testing import applyProfile


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
        migrate_simplefield(at_document, dx_document, 'subject', 'subject')
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

