from Acquisition import aq_inner
from DateTime import DateTime
from plone.app.contenttypes.behaviors.collection import (
    ICollection as ICollection_behavior,
)
from plone.app.contenttypes.interfaces import ICollection
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING
from plone.app.contenttypes.testing import set_browserlayer
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.textfield.value import RichTextValue
from plone.dexterity.interfaces import IDexterityFTI
from plone.testing.zope import Browser
from transaction import commit
from zope.component import createObject
from zope.component import queryUtility
from zope.interface import alsoProvides

import os.path
import unittest


query = [
    {
        "i": "Title",
        "o": "plone.app.querystring.operation.string.contains",
        "v": "Collection Test Page",
    }
]


def dummy_image():
    from plone.namedfile.file import NamedBlobImage

    filename = os.path.join(os.path.dirname(__file__), "image.png")
    with open(filename, "rb") as f:
        image_data = f.read()
    return NamedBlobImage(data=image_data, filename=filename)


class PloneAppCollectionClassTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory("Collection", "collection")
        self.collection = self.portal["collection"]

    def test_syndicatable(self):
        from plone.base.interfaces.syndication import ISyndicatable

        self.assertTrue(ISyndicatable.providedBy(self.collection))


class PloneAppCollectionIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]

        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory("Folder", "test-folder")
        self.folder = self.portal["test-folder"]

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name="Collection")
        schema = fti.lookupSchema()
        self.assertTrue(schema.getName().endswith("_0_Collection"))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name="Collection")
        self.assertNotEqual(None, fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name="Collection")
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(ICollection.providedBy(new_object))

    def test_adding(self):
        self.folder.invokeFactory("Collection", "collection1")
        p1 = self.folder["collection1"]
        self.assertTrue(ICollection.providedBy(p1))


class PloneAppCollectionViewsIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    def setUp(self):
        self.browser = Browser(self.layer["app"])
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        set_browserlayer(self.request)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory("Folder", "test-folder")
        self.folder = self.portal["test-folder"]
        self.folder.invokeFactory("Collection", "collection1")
        self.collection = aq_inner(self.folder["collection1"])
        self.request.set("URL", self.collection.absolute_url())
        self.request.set("ACTUAL_URL", self.collection.absolute_url())

    def test_collection_view(self):
        view = self.collection.restrictedTraverse("@@view")
        self.assertTrue(view())
        self.assertEqual(view.request.response.status, 200)

    def test_collection_listing_view(self):
        view = self.collection.restrictedTraverse("listing_view")
        self.assertTrue(view())
        self.assertEqual(view.request.response.status, 200)

    def test_collection_summary_view(self):
        view = self.collection.restrictedTraverse("summary_view")
        self.assertTrue(view())
        self.assertEqual(view.request.response.status, 200)

    def test_collection_full_view(self):
        view = self.collection.restrictedTraverse("full_view")
        self.assertTrue(view())
        self.assertEqual(view.request.response.status, 200)

    def test_collection_tabular_view(self):
        view = self.collection.restrictedTraverse("tabular_view")
        self.assertTrue(view())
        self.assertEqual(view.request.response.status, 200)

    def test_collection_album_view(self):
        view = self.collection.restrictedTraverse("album_view")
        self.assertTrue(view())
        self.assertEqual(view.request.response.status, 200)

    def test_add_collection(self):
        browser = self.browser
        browser.handleErrors = False
        browser.addHeader(
            "Authorization",
            "Basic {}:{}".format(
                SITE_OWNER_NAME,
                SITE_OWNER_PASSWORD,
            ),
        )
        portal_url = self.portal.absolute_url()
        browser.open(portal_url)
        browser.getLink(url="http://nohost/plone/++add++Collection").click()
        widget = "form.widgets.IDublinCore.title"
        browser.getControl(name=widget).value = "My collection"
        widget = "form.widgets.IDublinCore.description"
        browser.getControl(name=widget).value = "This is my collection."
        widget = "form.widgets.IRichTextBehavior.text"
        browser.getControl(name=widget).value = "Lorem Ipsum"
        widget = "form.widgets.IShortName.id"
        browser.getControl(name=widget).value = "my-special-collection"
        browser.getControl("Save").click()
        self.assertTrue(browser.url.endswith("my-special-collection/view"))
        self.assertTrue("My collection" in browser.contents)
        self.assertTrue("This is my collection" in browser.contents)
        self.assertTrue("Lorem Ipsum" in browser.contents)

    def test_collection_templates(self):
        self.portal.acl_users.userFolderAddUser(
            SITE_OWNER_NAME, SITE_OWNER_PASSWORD, ["Manager"], []
        )
        browser = self.browser
        portal = self.portal
        login(portal, SITE_OWNER_NAME)
        # add an image that will be listed by the collection
        portal.invokeFactory("Image", "image", title="Image example")

        image = self.portal["image"]
        image.image = dummy_image()

        # add a collection, so we can add a query to it
        portal.invokeFactory("Collection", "collection", title="New Collection")
        collection = portal["collection"]
        # Search for images
        query = [
            {
                "i": "Type",
                "o": "plone.app.querystring.operation.string.is",
                "v": "Image",
            }
        ]
        collection.text = RichTextValue(
            "Lorem collection ipsum", "text/plain", "text/html"
        )

        wrapped = ICollection_behavior(collection)
        # set the query and publish the collection
        wrapped.query = query
        workflow = portal.portal_workflow
        workflow.doActionFor(collection, "publish")
        commit()
        logout()
        # open a browser to see if our image is in the results
        browser.handleErrors = False
        url = collection.absolute_url()
        browser.open(url)
        self.assertIn("Lorem collection ipsum", browser.contents)
        self.assertIn("Image example", browser.contents)

        # open summary_view template
        browser.open(f"{url}/@@summary_view")
        self.assertIn("Lorem collection ipsum", browser.contents)
        self.assertIn("Image example", browser.contents)

        # open full_view template
        browser.open(f"{url}/@@full_view")
        self.assertIn("Lorem collection ipsum", browser.contents)
        self.assertIn("Image example", browser.contents)

        # open tabular_view template
        browser.open(f"{url}/@@tabular_view")
        self.assertIn("Lorem collection ipsum", browser.contents)
        self.assertIn("Image example", browser.contents)

        # open thumbnail_view template
        browser.open(f"{url}/@@album_view")
        self.assertIn("Lorem collection ipsum", browser.contents)
        self.assertIn("Image example", browser.contents)

    def test_sorting_1(self):
        self.portal.acl_users.userFolderAddUser(
            SITE_OWNER_NAME, SITE_OWNER_PASSWORD, ["Manager"], []
        )

        portal = self.portal
        login(portal, SITE_OWNER_NAME)
        query = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.string.is",
                "v": "News Item",
            }
        ]
        portal.invokeFactory(
            "Collection",
            "collection",
            title="New Collection",
            query=query,
            sort_on="created",
            sort_reversed=True,
        )

        now = DateTime()
        # News Item 1
        portal.invokeFactory(id="newsitem1", type_name="News Item")
        item1 = portal.newsitem1
        item1.creation_date = now - 2
        item1.reindexObject()
        # News Item 2
        portal.invokeFactory(id="newsitem2", type_name="News Item")
        item2 = portal.newsitem2
        item2.creation_date = now - 1
        item2.reindexObject()
        # News Item 3
        portal.invokeFactory(id="newsitem3", type_name="News Item")
        item3 = portal.newsitem3
        item3.creation_date = now
        item3.reindexObject()

        collection = portal["collection"]
        wrapped = ICollection_behavior(collection)
        results = wrapped.results(batch=False)
        ritem0 = results[0]
        ritem1 = results[1]
        ritem2 = results[2]

        self.assertTrue(ritem0.CreationDate() > ritem1.CreationDate())
        self.assertTrue(ritem1.CreationDate() > ritem2.CreationDate())

    def test_custom_query(self):
        self.portal.acl_users.userFolderAddUser(
            SITE_OWNER_NAME, SITE_OWNER_PASSWORD, ["Manager"], []
        )
        portal = self.portal
        login(portal, SITE_OWNER_NAME)
        query = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.string.is",
                "v": ["News Item", "Document"],
            }
        ]
        portal.invokeFactory(
            "Collection",
            "collection",
            title="New Collection",
            query=query,
        )

        # item 1
        portal.invokeFactory(id="testnews", type_name="News Item")
        item1 = portal.testnews
        item1.reindexObject()

        # item 2
        portal.invokeFactory(id="testdoc", type_name="Document")
        item2 = portal.testdoc
        item2.reindexObject()

        collection = portal["collection"]
        wrapped = ICollection_behavior(collection)

        # Test unmodified query
        results = wrapped.results(batch=False)
        self.assertEqual(len(results), 2)

        # Test with custom query
        results = wrapped.results(batch=False, custom_query={"portal_type": "Document"})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "testdoc")

        # Test with custom query, which should not find anything
        results = wrapped.results(
            batch=False, custom_query={"portal_type": "Document", "id": "bla"}
        )
        self.assertEqual(len(results), 0)

    def test_respect_navigation_root(self):
        self.portal.acl_users.userFolderAddUser(
            SITE_OWNER_NAME, SITE_OWNER_PASSWORD, ["Manager"], []
        )
        portal = self.portal
        login(portal, SITE_OWNER_NAME)

        # Create two subsites i.e create two folders and mark them with
        # INavigationRoot
        for i in range(1, 3):
            folder_id = f"folder{i}"
            portal.invokeFactory("Folder", folder_id, title=f"Folder{i}")
            folder = portal[folder_id]
            alsoProvides(folder, INavigationRoot)
        folders = (portal["folder1"], portal["folder2"])

        # Add a content item to each folder
        for f in folders:
            f_id = f.getId()
            f.invokeFactory("Document", f"item_in_{f_id}", title=f"Item In {f_id}")

        # Add a collection to folder1
        folder1 = folders[0]
        folder1.invokeFactory("Collection", "collection1", title="Collection 1")
        collection1 = folder1["collection1"]
        wrapped = ICollection_behavior(collection1)
        wrapped.query = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.string.is",
                "v": "Document",
            },
            # use a "/" path and navroot works fine!
            {
                "i": "path",
                "o": "plone.app.querystring.operation.string.path",
                "v": "/",
            },
        ]

        # Check if only the item inside folder1 is returned, since it's a
        # navigation root.
        items = wrapped.results(batch=False)
        ids = [i.getId() for i in items]
        self.assertListEqual(ids, ["item_in_folder1"])


class PloneAppCollectionEditViewsIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        set_browserlayer(self.request)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory("Folder", "test-folder")
        self.folder = self.portal["test-folder"]
        self.folder.invokeFactory("Collection", "collection1")
        self.collection = aq_inner(self.folder["collection1"])
        self.request.set("URL", self.collection.absolute_url())
        self.request.set("ACTUAL_URL", self.collection.absolute_url())

    def test_search_result(self):
        view = self.collection.restrictedTraverse("@@edit")
        html = view()
        self.assertTrue("form-widgets-ICollection-query" in html)
        # from plone.app.contentlisting.interfaces import IContentListing
        # self.assertTrue(IContentListing.providedBy(view.accessor()))
        # self.assertTrue(getattr(accessor(), 'actual_result_count'))
        # self.assertEqual(accessor().actual_result_count, 0)
