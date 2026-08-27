from plone.app.contenttypes.interfaces import IFolder
from plone.app.contenttypes.testing import (  # noqa
    PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING,
)
from plone.app.contenttypes.testing import (  # noqa
    PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING,
)
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from plone.testing.zope import Browser
from zope.component import createObject
from zope.component import queryUtility

import unittest


class FolderIntegrationTest(unittest.TestCase):
    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.request["ACTUAL_URL"] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name="Folder")
        schema = fti.lookupSchema()
        self.assertTrue(schema.getName().endswith("_0_Folder"))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name="Folder")
        self.assertNotEqual(None, fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name="Folder")
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(IFolder.providedBy(new_object))

    def test_adding(self):
        self.portal.invokeFactory("Folder", "doc1")
        self.assertTrue(IFolder.providedBy(self.portal["doc1"]))


class FolderFunctionalTest(unittest.TestCase):
    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization",
            "Basic {}:{}".format(
                SITE_OWNER_NAME,
                SITE_OWNER_PASSWORD,
            ),
        )

    def test_add_folder(self):
        self.browser.open(self.portal_url)
        self.browser.getLink(url="http://nohost/plone/++add++Folder").click()
        widget = "form.widgets.IDublinCore.title"
        self.browser.getControl(name=widget).value = "My folder"
        widget = "form.widgets.IShortName.id"
        self.browser.getControl(name=widget).value = ""
        widget = "form.widgets.IDublinCore.description"
        self.browser.getControl(name=widget).value = "This is my folder."
        self.browser.getControl("Save").click()
        self.assertTrue(self.browser.url.endswith("my-folder/view"))
        self.assertTrue("My folder" in self.browser.contents)
        self.assertTrue("This is my folder" in self.browser.contents)

    def test_add_folder_with_shortname(self):
        self.browser.open(self.portal_url)
        self.browser.getLink(url="http://nohost/plone/++add++Folder").click()
        widget = "form.widgets.IDublinCore.title"
        self.browser.getControl(name=widget).value = "My folder"
        widget = "form.widgets.IShortName.id"
        self.browser.getControl(name=widget).value = "my-special-folder"
        self.browser.getControl("Save").click()
        self.assertTrue(self.browser.url.endswith("my-special-folder/view"))
