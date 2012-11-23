# -*- coding: utf-8 -*-
import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser

from plone.app.contenttypes.interfaces import IFolder

from plone.app.contenttypes.testing import (
    PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING,
    PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING
)

from plone.app.testing import TEST_USER_ID, setRoles


class FolderIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_schema(self):
        fti = queryUtility(
            IDexterityFTI,
            name='Folder')
        schema = fti.lookupSchema()
        self.assertEqual(schema.getName(), 'plone_0_Folder')

    def test_fti(self):
        fti = queryUtility(
            IDexterityFTI,
            name='Folder'
        )
        self.assertNotEquals(None, fti)

    def test_factory(self):
        fti = queryUtility(
            IDexterityFTI,
            name='Folder'
        )
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IFolder.providedBy(new_object))

    def test_adding(self):
        self.portal.invokeFactory(
            'Folder',
            'doc1'
        )
        self.assertTrue(IFolder.providedBy(self.portal['doc1']))


class FolderViewIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'folder')
        folder = self.portal['folder']
        folder.title = "My Folder"
        folder.description = "This is my folder."
        self.folder = folder
        self.request.set('URL', folder.absolute_url())
        self.request.set('ACTUAL_URL', folder.absolute_url())

    def test_folder_view(self):
        view = self.folder.restrictedTraverse('@@view')

        self.assertTrue(view())
        self.assertTrue('My Folder' in view())
        self.assertTrue('This is my folder.' in view())

    def test_folder_summary_view(self):
        view = self.folder.restrictedTraverse('folder_summary_view')

        self.assertTrue(view())
        self.assertTrue('My Folder' in view())
        self.assertTrue('This is my folder.' in view())

    def test_folder_full_view(self):
        view = self.folder.restrictedTraverse('folder_full_view')

        self.assertTrue(view())
        self.assertTrue('My Folder' in view())
        self.assertTrue('This is my folder.' in view())

    def test_folder_tabular_view(self):
        view = self.folder.restrictedTraverse('folder_tabular_view')

        self.assertTrue(view())
        self.assertTrue('My Folder' in view())
        self.assertTrue('This is my folder.' in view())

    def test_atct_album_view(self):
        view = self.folder.restrictedTraverse('atct_album_view')
        self.assertTrue(view())
        self.assertTrue('My Folder' in view())
        self.assertTrue('This is my folder.' in view())


class FolderFunctionalText(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def test_add_folder(self):
        self.browser.open(self.portal_url)
        self.browser.getLink('Folder').click()
        self.assertTrue('Title' in self.browser.contents)
        self.assertTrue('Description' in self.browser.contents)
        self.assertTrue('Text' in self.browser.contents)
        self.browser.getControl(name='form.widgets.IDublinCore.title')\
            .value = "My folder"
        self.browser.getControl(name='form.widgets.IDublinCore.description')\
            .value = "This is my folder."
        self.browser.getControl('Save').click()
        self.assertTrue(self.browser.url.endswith('my-folder/view'))
        self.assertTrue('My folder' in self.browser.contents)
        self.assertTrue('This is my folder' in self.browser.contents)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
