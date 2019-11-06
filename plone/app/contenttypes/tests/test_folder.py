# -*- coding: utf-8 -*-
from plone.app.contenttypes.browser.folder import FolderView
from plone.app.contenttypes.interfaces import IFolder
from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING  # noqa
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING  # noqa
from plone.app.contenttypes.tests.test_image import dummy_image
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from plone.testing.z2 import Browser
from zope.interface import alsoProvides
from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.fti import DexterityFTI
import transaction
import unittest


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
        self.assertNotEqual(None, fti)

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


class FolderViewIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])

    def test_result_filtering(self):
        """Test, if portal_state's friendly_types and the result method's
        keyword arguments are included in the query.
        """

        self.portal.invokeFactory('News Item', 'newsitem')
        self.portal.invokeFactory('Document', 'document')
        view = FolderView(self.portal, self.request)

        # Test, if all results are found.
        view.portal_state.friendly_types = lambda: ['Document', 'News Item']
        res = view.results()
        self.assertEqual(len(res), 2)

        # Test, if friendly_types does filter for types.
        view.portal_state.friendly_types = lambda: ['Document']
        res = view.results()
        self.assertEqual(len(res), 1)

        # Test, if friendly_types does filter for types.
        view.portal_state.friendly_types = lambda: ['NotExistingType']
        res = view.results()
        self.assertEqual(len(res), 0)

        # Test, if kwargs filtering is applied.
        view.portal_state.friendly_types = lambda: ['NotExistingType']
        res = view.results(
            object_provides='plone.app.contenttypes.interfaces.IDocument'
        )
        self.assertEqual(len(res), 1)


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
            'Basic {0}:{1}'.format(SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def test_add_folder(self):
        self.browser.open(self.portal_url)
        self.browser.getLink(url='http://nohost/plone/++add++Folder').click()
        widget = 'form.widgets.IDublinCore.title'
        self.browser.getControl(name=widget).value = 'My folder'
        widget = 'form.widgets.IShortName.id'
        self.browser.getControl(name=widget).value = ''
        widget = 'form.widgets.IDublinCore.description'
        self.browser.getControl(name=widget).value = 'This is my folder.'
        self.browser.getControl('Save').click()
        self.assertTrue(self.browser.url.endswith('my-folder/view'))
        self.assertTrue('My folder' in self.browser.contents)
        self.assertTrue('This is my folder' in self.browser.contents)

    def test_add_folder_with_shortname(self):
        self.browser.open(self.portal_url)
        self.browser.getLink(url='http://nohost/plone/++add++Folder').click()
        widget = 'form.widgets.IDublinCore.title'
        self.browser.getControl(name=widget).value = 'My folder'
        widget = 'form.widgets.IShortName.id'
        self.browser.getControl(name=widget).value = 'my-special-folder'
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
        transaction.commit()
        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic {0}:{1}'.format(SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def test_folder_view(self):
        self.browser.open(self.folder_url + '/view')
        self.assertIn('My Folder', self.browser.contents)
        self.assertIn('Document 1', self.browser.contents)

    def test_folder_summary_view(self):
        self.browser.open(self.folder_url + '/summary_view')
        self.assertIn('My Folder', self.browser.contents)
        self.assertIn('Document 1', self.browser.contents)

    def test_folder_full_view(self):
        self.browser.open(self.folder_url + '/full_view')
        self.assertIn('My Folder', self.browser.contents)
        self.assertIn('Document 1', self.browser.contents)

    def test_folder_tabular_view(self):
        self.browser.open(self.folder_url + '/tabular_view')
        self.assertIn('My Folder', self.browser.contents)
        self.assertIn('Document 1', self.browser.contents)

    def test_folder_album_view(self):
        self.folder.invokeFactory('Image', id='image1', title='Image 1')
        img1 = self.folder['image1']
        img1.image = dummy_image()
        transaction.commit()
        self.browser.open(self.folder_url + '/album_view')
        self.assertIn('My Folder', self.browser.contents)
        self.assertIn(
            '<img src="http://nohost/plone/folder/image1/@@images',
            self.browser.contents)

    def test_folder_album_view_newsitem_ileadimage(self):
        self.folder.invokeFactory('News Item', id='newsitem1', title='My Newsitem')
        newsitem1 = self.folder['newsitem1']
        newsitem1.image = dummy_image()
        transaction.commit()
        self.browser.open(self.folder_url + '/album_view')
        self.assertIn('My Folder', self.browser.contents)
        self.assertIn(
            '<img src="http://nohost/plone/folder/newsitem1/@@images',
            self.browser.contents)

        # Folder should show up in the portal album view with the news item image.
        self.browser.open(self.portal_url + '/album_view')
        browser_no_whitespace = self.browser.contents.replace(" ", "").replace("\n", "")
        self.assertIn('MyFolder(1)', browser_no_whitespace)
        self.assertIn('My Newsitem', self.browser.contents)
        self.assertIn(
            '<img src="http://nohost/plone/folder/newsitem1/@@images',
            self.browser.contents)

    def _add_leadimage_to_folder_fti_and_create_folder(self):
        # Change the Folder FTI to have a leadimage, and create one.
        fti = self.portal.portal_types.Folder
        behaviors = list(fti.behaviors)
        behaviors.append('plone.app.contenttypes.behaviors.leadimage.ILeadImage'),
        fti.behaviors = tuple(behaviors)
        self.folder.invokeFactory(
            'Folder',
            id='leadimagefolder',
            title=u'Folder with a lead image'
        )
        leadimagefolder = self.folder['leadimagefolder']
        leadimagefolder.image = dummy_image()
        transaction.commit()
        return leadimagefolder

    def test_folder_album_view_ileadimage_folder_without_image_object(self):
        self._add_leadimage_to_folder_fti_and_create_folder()
        # The folder with lead image should end up in the album view of the parent folder.
        # Preferably under images, because it has its own image.
        self.browser.open(self.folder_url + '/album_view')
        self.assertIn('Folder with a lead image', self.browser.contents)
        # If our logic is off, it could end up under folders instead,
        # with an image count of probably zero.
        browser_no_whitespace = self.browser.contents.replace(" ", "").replace("\n", "")
        self.assertNotIn('Folderwithaleadimage(', browser_no_whitespace)
        self.assertIn(
            '<img src="http://nohost/plone/folder/leadimagefolder/@@images',
            self.browser.contents)
        # But it definitely should not be there twice.
        self.assertEqual(1, self.browser.contents.count('leadimagefolder/@@images'))

    def test_folder_album_view_ileadimage_folder_with_image_object(self):
        leadimagefolder = self._add_leadimage_to_folder_fti_and_create_folder()

        # add an image to the leadimagefolder
        leadimagefolder.invokeFactory('Image', id='image2', title='Image 2')
        img2 = leadimagefolder['image2']
        img2.image = dummy_image()
        transaction.commit()

        # The folder with lead image should end up in the album view of the parent folder.
        self.browser.open(self.folder_url + '/album_view')
        self.assertIn('Folder with a lead image', self.browser.contents)
        # It should be under folders, with an image count.
        browser_no_whitespace = self.browser.contents.replace(" ", "").replace("\n", "")
        self.assertIn('Folderwithaleadimage(1)', browser_no_whitespace)
        self.assertIn(
            '<img src="http://nohost/plone/folder/leadimagefolder/@@images',
            self.browser.contents)
        # The image should be there only once.
        self.assertEqual(1, self.browser.contents.count('leadimagefolder/@@images'))

    def _create_leadimage_fti_and_folder(self):
        # Register a folderish FTI with leadimage, and create one.
        fti = DexterityFTI('leadimagefolder')
        self.portal.portal_types._setObject('leadimagefolder', fti)
        fti.klass = 'plone.dexterity.content.Container'
        fti.behaviors = (
            'plone.app.contenttypes.behaviors.leadimage.ILeadImage',
        )
        fti.global_allow = True
        fti.filter_content_types = False
        self.folder.invokeFactory(
            'leadimagefolder',
            id='leadimagefolder',
            title=u'Folder with a lead image'
        )
        leadimagefolder = self.folder['leadimagefolder']
        leadimagefolder.image = dummy_image()
        transaction.commit()
        return leadimagefolder

    def test_folder_album_view_ileadimage_custom_folder_without_image_object(self):
        self._create_leadimage_fti_and_folder()
        # The folder with lead image should end up in the album view of the parent folder.
        # Preferably under images, because it has its own image.
        self.browser.open(self.folder_url + '/album_view')
        self.assertIn('Folder with a lead image', self.browser.contents)
        # If our logic is off, it could end up under folders instead,
        # with an image count of probably zero.
        # But currently this does not happen, because it is not an IFolder.
        browser_no_whitespace = self.browser.contents.replace(" ", "").replace("\n", "")
        self.assertNotIn('Folderwithaleadimage(', browser_no_whitespace)
        self.assertIn(
            '<img src="http://nohost/plone/folder/leadimagefolder/@@images',
            self.browser.contents)
        # But it definitely should not be there twice.
        self.assertEqual(1, self.browser.contents.count('leadimagefolder/@@images'))

    def test_folder_album_view_ileadimage_custom_folder_with_image_object(self):
        leadimagefolder = self._create_leadimage_fti_and_folder()

        # add an image to the leadimagefolder
        leadimagefolder.invokeFactory('Image', id='image2', title='Image 2')
        img2 = leadimagefolder['image2']
        img2.image = dummy_image()
        transaction.commit()

        # The folder with lead image should end up in the album view of the parent folder.
        self.browser.open(self.folder_url + '/album_view')
        self.assertIn('Folder with a lead image', self.browser.contents)
        # It should be under folders, with an image count.
        # But currently this does not happen, because it is not an IFolder.
        # browser_no_whitespace = self.browser.contents.replace(" ", "").replace("\n", "")
        # self.assertIn('Folderwithaleadimage(1)', browser_no_whitespace)
        self.assertIn(
            '<img src="http://nohost/plone/folder/leadimagefolder/@@images',
            self.browser.contents)
        # The image should be there only once.
        self.assertEqual(1, self.browser.contents.count('leadimagefolder/@@images'))

    def test_list_item_wout_title(self):
        """In content listings, if a content object has no title use it's id.
        """
        self.folder.invokeFactory('Document', id='doc_wout_title')
        transaction.commit()

        # Document should be shown in listing view (and it's siblings)
        self.browser.open(self.folder_url + "/listing_view")
        self.assertIn('doc_wout_title', self.browser.contents)

        # And also in tabular view
        self.browser.open(self.folder_url + "/tabular_view")
        self.assertIn('doc_wout_title', self.browser.contents)
