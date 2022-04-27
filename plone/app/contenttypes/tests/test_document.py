from plone.app.contenttypes.interfaces import IDocument
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
from plone.app.textfield.value import RichTextValue
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.dexterity.interfaces import IDexterityFTI
from plone.testing.zope import Browser
from zope.component import createObject
from zope.component import queryUtility
from zope.interface import alsoProvides

import unittest


class DocumentIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.request["ACTUAL_URL"] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name="Document")
        schema = fti.lookupSchema()
        self.assertTrue(schema.getName().endswith("_0_Document"))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name="Document")
        self.assertNotEqual(None, fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name="Document")
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(IDocument.providedBy(new_object))

    def test_adding(self):
        self.portal.invokeFactory("Document", "doc1")
        self.assertTrue(IDocument.providedBy(self.portal["doc1"]))

    def test_view(self):
        self.portal.invokeFactory("Document", "document")
        document = self.portal["document"]
        document.title = "My Document"
        document.description = "This is my document."
        document.text = RichTextValue(
            "Lorem ipsum",
            "text/plain",
            "text/html",
        )
        self.request.set("URL", document.absolute_url())
        self.request.set("ACTUAL_URL", document.absolute_url())
        alsoProvides(self.request, IPloneFormLayer)
        view = document.restrictedTraverse("@@view")
        self.assertEqual(view.request.response.status, 200)
        output = view()
        self.assertTrue(output)
        self.assertTrue("My Document" in output)
        self.assertTrue("This is my document." in output)
        self.assertTrue("Lorem ipsum" in output)

    def tearDown(self):
        if "document" in self.portal.objectIds():
            self.portal.manage_delObjects(ids="document")


class DocumentFunctionalTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
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

    def test_add_document(self):
        self.browser.open(self.portal_url)
        self.browser.getLink(url="http://nohost/plone/++add++Document").click()
        widget = "form.widgets.IDublinCore.title"
        self.browser.getControl(name=widget).value = "My document"
        widget = "form.widgets.IDublinCore.description"
        self.browser.getControl(name=widget).value = "This is my document."
        widget = "form.widgets.IRichTextBehavior.text"
        self.browser.getControl(name=widget).value = "Lorem Ipsum"
        widget = "form.widgets.IShortName.id"
        self.browser.getControl(name=widget).value = "my-special-document"
        self.browser.getControl("Save").click()
        self.assertTrue(self.browser.url.endswith("my-special-document/view"))
        self.assertTrue("My document" in self.browser.contents)
        self.assertTrue("This is my document" in self.browser.contents)
        self.assertTrue("Lorem Ipsum" in self.browser.contents)
