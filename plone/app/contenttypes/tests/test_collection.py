# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from DateTime import DateTime

import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility
from zope.interface import alsoProvides
from transaction import commit

from plone.dexterity.interfaces import IDexterityFTI

from plone.app.contenttypes.testing import \
    PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING
from plone.app.contenttypes.testing import \
    PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, \
    setRoles, login, logout

from plone.app.contenttypes.interfaces import ICollection
from plone.app.contenttypes.behaviors.collection import ICollection as \
    ICollection_behavior

from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.textfield.value import RichTextValue
import os.path

query = [{
    'i': 'Title',
    'o': 'plone.app.querystring.operation.string.contains',
    'v': 'Collection Test Page',
}]


def dummy_image():
    from plone.namedfile.file import NamedBlobImage
    filename = os.path.join(os.path.dirname(__file__), u'image.png')
    return NamedBlobImage(
        data=open(filename, 'r').read(),
        filename=filename
    )


class PloneAppCollectionClassTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Collection', 'collection')
        self.collection = self.portal['collection']

    def test_bbb_listMetaDataFields(self):
        self.assertEqual(self.collection.listMetaDataFields(), [])

    def test_results(self):
        pass

    def test_bbb_selectedViewFields(self):
        self.assertEqual(self.collection.selectedViewFields(), [])
        self.collection.customViewFields = ['Title', 'Description']
        self.assertEqual(self.collection.selectedViewFields(),
                         [('Title', 'Title'), ('Description', 'Description')])

    def test_getFoldersAndImages(self):
        pass

    def test_bbb_setQuery(self):
        self.collection.setQuery(query)
        self.assertEqual(self.collection.query, query)

    def test_bbb_getQuery(self):
        self.collection.query = query
        self.assertEqual(self.collection.getQuery(), query)

    def test_bbb_setSort_on(self):
        self.collection.setSort_on('start')
        self.assertEqual(self.collection.sort_on, 'start')

    def test_bbb_setSort_reversed(self):
        self.collection.setSort_reversed(True)
        self.assertEqual(self.collection.sort_reversed, True)

    def test_syndicatable(self):
        from Products.CMFPlone.interfaces.syndication import ISyndicatable
        self.assertTrue(ISyndicatable.providedBy(self.collection))


class PloneAppCollectionIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']

    def test_schema(self):
        fti = queryUtility(IDexterityFTI,
                           name='Collection')
        schema = fti.lookupSchema()
        self.assertEqual(schema.getName(), 'plone_0_Collection')

    def test_fti(self):
        fti = queryUtility(IDexterityFTI,
                           name='Collection')
        self.assertNotEquals(None, fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI,
                           name='Collection')
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(ICollection.providedBy(new_object))

    def test_adding(self):
        self.folder.invokeFactory('Collection',
                                  'collection1')
        p1 = self.folder['collection1']
        self.assertTrue(ICollection.providedBy(p1))


class PloneAppCollectionViewsIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']
        self.folder.invokeFactory('Collection',
                                  'collection1')
        self.collection = aq_inner(self.folder['collection1'])
        self.request.set('URL', self.collection.absolute_url())
        self.request.set('ACTUAL_URL', self.collection.absolute_url())

    def test_view(self):
        view = self.collection.restrictedTraverse('@@view')
        self.assertTrue(view())
        self.assertEqual(view.request.response.status, 200)

    def test_standard_view(self):
        view = self.collection.restrictedTraverse('standard_view')
        self.assertTrue(view())
        self.assertEqual(view.request.response.status, 200)

    def test_summary_view(self):
        view = self.collection.restrictedTraverse('summary_view')
        self.assertTrue(view())
        self.assertEqual(view.request.response.status, 200)

    def test_all_content(self):
        view = self.collection.restrictedTraverse('all_content')
        self.assertTrue(view())
        self.assertEqual(view.request.response.status, 200)

    def test_tabular_view(self):
        view = self.collection.restrictedTraverse('tabular_view')
        self.assertTrue(view())
        self.assertEqual(view.request.response.status, 200)

    def test_thumbnail_view(self):
        view = self.collection.restrictedTraverse('thumbnail_view')
        self.assertTrue(view())
        self.assertEqual(view.request.response.status, 200)

    # @unittest.skip("Needs to be refactored")
    def test_collection_templates(self):
        portal = self.layer['portal']
        login(portal, 'admin')
        # add an image that will be listed by the collection
        portal.invokeFactory("Image",
                             "image",
                             title="Image example")

        image = self.portal['image']
        image.image = dummy_image()

        # add a collection, so we can add a query to it
        portal.invokeFactory("Collection",
                             "collection",
                             title="New Collection")
        collection = portal['collection']
        # Search for images
        query = [{
            'i': 'Type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'Image',
        }]
        collection.text = RichTextValue(
            u"Lorem collection ipsum",
            'text/plain',
            'text/html'
        )

        wrapped = ICollection_behavior(collection)
        # set the query and publish the collection
        wrapped.query = query
        workflow = portal.portal_workflow
        workflow.doActionFor(collection, "publish")
        commit()
        logout()
        # open a browser to see if our image is in the results
        browser = Browser(self.layer['app'])
        browser.handleErrors = False
        url = collection.absolute_url()
        browser.open(url)
        self.assertTrue("Lorem collection ipsum" in browser.contents)
        self.assertTrue("Image example" in browser.contents)

        # open summary_view template
        browser.open('%s/@@summary_view' % url)
        self.assertTrue("Lorem collection ipsum" in browser.contents)
        self.assertTrue("Image example" in browser.contents)

        # open all_content template
        browser.open('%s/@@all_content' % url)
        self.assertTrue("Lorem collection ipsum" in browser.contents)
        self.assertTrue("Image example" in browser.contents)

        # open tabular_view template
        browser.open('%s/@@tabular_view' % url)
        self.assertTrue("Lorem collection ipsum" in browser.contents)
        self.assertTrue("Image example" in browser.contents)

        # open thumbnail_view template
        browser.open('%s/@@thumbnail_view' % url)
        self.assertTrue("Lorem collection ipsum" in browser.contents)
        self.assertTrue("Image example" in browser.contents)

    def test_sorting_1(self):
        portal = self.layer['portal']
        login(portal, 'admin')
        query = [{
            'i': 'portal_type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'News Item',
        }]
        portal.invokeFactory("Collection",
                             "collection",
                             title="New Collection",
                             query=query,
                             sort_on='created',
                             sort_reversed=True,
                             )

        now = DateTime()
        # News Item 1
        portal.invokeFactory(id='newsitem1',
                             type_name='News Item')
        item1 = portal.newsitem1
        item1.creation_date = now - 2
        item1.reindexObject()
        # News Item 2
        portal.invokeFactory(id='newsitem2',
                             type_name='News Item')
        item2 = portal.newsitem2
        item2.creation_date = now - 1
        item2.reindexObject()
        # News Item 3
        portal.invokeFactory(id='newsitem3',
                             type_name='News Item')
        item3 = portal.newsitem3
        item3.creation_date = now
        item3.reindexObject()

        collection = portal['collection']
        wrapped = ICollection_behavior(collection)
        results = wrapped.results(batch=False)
        ritem0 = results[0]
        ritem1 = results[1]
        ritem2 = results[2]

        self.assertTrue(ritem0.CreationDate() > ritem1.CreationDate())
        self.assertTrue(ritem1.CreationDate() > ritem2.CreationDate())

    def test_getFoldersAndImages(self):
        portal = self.layer['portal']
        login(portal, 'admin')
        # add a collection, so we can add a query to it
        portal.invokeFactory("Collection",
                             "collection",
                             title="New Collection")

        # add example folder and a subfolder to it, both with same id
        portal.invokeFactory("Folder",
                             "folder1",
                             title="Folder1")
        folder = portal['folder1']

        folder.invokeFactory("Folder",
                             "folder1",
                             title="Folder1")
        subfolder = folder['folder1']
        # add example image into folder and its subfolder
        folder.invokeFactory("Image",
                             "image",
                             title="Image example")

        subfolder.invokeFactory("Image",
                                "another_image",
                                title="Image example")
        query = [{
            'i': 'Type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'Folder',
        }]
        collection = portal['collection']
        wrapped = ICollection_behavior(collection)
        wrapped.query = query
        imagecount = wrapped.getFoldersAndImages()['total_number_of_images']
        # The current implementation for getFoldersAndImages will return
        # another_image under subfolder and also under folder
        self.assertEqual(imagecount, 3)

    def test_getFoldersAndImages_returning_images(self):
        portal = self.layer['portal']
        login(portal, 'admin')
        # add a collection, so we can add a query to it
        portal.invokeFactory("Collection",
                             "collection",
                             title="New Collection")

        # add example folder
        portal.invokeFactory("Folder",
                             "folder1",
                             title="Folder1")
        folder = portal['folder1']

        # add example image into this folder
        folder.invokeFactory("Image",
                             "image",
                             title="Image example")

        # add another image into the portal root
        portal.invokeFactory("Image",
                             "image",
                             title="Image example")
        query = [{
            'i': 'Type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'Image',
        }]
        collection = portal['collection']
        wrapped = ICollection_behavior(collection)
        wrapped.query = query
        imagecount = wrapped.getFoldersAndImages()['total_number_of_images']
        self.assertEqual(imagecount, 2)

    def test_respect_navigation_root(self):
        portal = self.layer['portal']
        login(portal, 'admin')

        # Create two subsites i.e create two folders and mark them with
        # INavigationRoot
        for i in xrange(1, 3):
            folder_id = 'folder{}'.format(i)
            portal.invokeFactory('Folder',
                                 folder_id,
                                 title='Folder{}'.format(i))
            folder = portal[folder_id]
            alsoProvides(folder, INavigationRoot)
        folders = (portal['folder1'], portal['folder2'])

        # Add a content item to each folder
        for f in folders:
            f_id = f.getId()
            f.invokeFactory('Document',
                            'item_in_{}'.format(f_id),
                            title='Item In {}'.format(f_id))

        # Add a collection to folder1
        folder1 = folders[0]
        folder1.invokeFactory('Collection',
                              'collection1',
                              title='Collection 1')
        collection1 = folder1['collection1']
        wrapped = ICollection_behavior(collection1)
        wrapped.query = [{
            'i': 'portal_type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'Document',
        }]

        # Check if only the item inside folder1 is returned, since it's a
        # navigation root.
        items = wrapped.results(batch=False)
        ids = [i.getId() for i in items]
        self.assertListEqual(ids, ['item_in_folder1'])


class PloneAppCollectionEditViewsIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']
        self.folder.invokeFactory(
            'Collection',
            'collection1'
        )
        self.collection = aq_inner(self.folder['collection1'])
        self.request.set('URL', self.collection.absolute_url())
        self.request.set('ACTUAL_URL', self.collection.absolute_url())

    def test_search_result(self):
        view = self.collection.restrictedTraverse('@@edit')
        html = view()
        self.assertTrue('form-widgets-ICollection-query' in html)
        #from plone.app.contentlisting.interfaces import IContentListing
        #self.assertTrue(IContentListing.providedBy(view.accessor()))
        #self.assertTrue(getattr(accessor(), "actual_result_count"))
        #self.assertEqual(accessor().actual_result_count, 0)
