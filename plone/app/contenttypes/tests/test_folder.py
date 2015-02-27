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
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])

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
        self.assertTrue(IFolder.providedBy(new_object))

    def test_adding(self):
        self.portal.invokeFactory(
            'Folder',
            'doc1'
        )
        self.assertTrue(IFolder.providedBy(self.portal['doc1']))


class FolderFunctionalTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def test_add_folder(self):
        self.browser.open(self.portal_url)
        self.browser.getLink(url='http://nohost/plone/++add++Folder').click()
        self.browser.getControl(name='form.widgets.IDublinCore.title')\
            .value = "My folder"
        self.browser.getControl(name='form.widgets.IShortName.id')\
            .value = ""
        self.browser.getControl(name='form.widgets.IDublinCore.description')\
            .value = "This is my folder."
        self.browser.getControl('Save').click()
        self.assertTrue(self.browser.url.endswith('my-folder/view'))
        self.assertTrue('My folder' in self.browser.contents)
        self.assertTrue('This is my folder' in self.browser.contents)

    def test_add_folder_with_shortname(self):
        self.browser.open(self.portal_url)
        self.browser.getLink(url='http://nohost/plone/++add++Folder').click()
        self.browser.getControl(name='form.widgets.IDublinCore.title')\
            .value = "My folder"
        self.browser.getControl(name='form.widgets.IShortName.id')\
            .value = "my-special-folder"
        self.browser.getControl('Save').click()
        self.assertTrue(self.browser.url.endswith('my-special-folder/view'))


class FolderViewFunctionalTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal_url = self.portal.absolute_url()
        self.portal.invokeFactory('Folder', id='folder', title='My Folder')
        self.folder = self.portal.folder
        self.folder_url = self.folder.absolute_url()
        self.folder.invokeFactory('Document', id='doc1', title='Document 1')
        import transaction
        transaction.commit()
        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def test_folder_view(self):
        self.browser.open(self.folder_url + '/view')
        self.assertTrue('My Folder' in self.browser.contents)
        self.assertTrue('Document 1' in self.browser.contents)

    def test_folder_summary_view(self):
        self.browser.open(self.folder_url + '/summary_view')
        self.assertTrue('My Folder' in self.browser.contents)
        self.assertTrue('Document 1' in self.browser.contents)

    def test_folder_full_view(self):
        self.browser.open(self.folder_url + '/full_view')
        self.assertTrue('My Folder' in self.browser.contents)
        self.assertTrue('Document 1' in self.browser.contents)

    def test_folder_tabular_view(self):
        self.browser.open(self.folder_url + '/tabular_view')
        self.assertTrue('My Folder' in self.browser.contents)
        self.assertTrue('Document 1' in self.browser.contents)

    def test_folder_album_view(self):
        self.browser.open(self.folder_url + '/album_view')
        self.assertTrue('My Folder' in self.browser.contents)
        self.assertTrue('Document 1' in self.browser.contents)
