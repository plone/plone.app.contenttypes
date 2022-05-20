from plone.app.contenttypes.interfaces import IImage
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
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.dexterity.interfaces import IDexterityFTI
from plone.testing.zope import Browser
from zope.component import createObject
from zope.component import queryUtility
from zope.interface import alsoProvides

import io
import os.path
import unittest


def dummy_image(filename="image.jpg"):
    from plone.namedfile.file import NamedBlobImage

    filename = os.path.join(os.path.dirname(__file__), filename)
    with open(filename, "rb") as f:
        image_data = f.read()
    return NamedBlobImage(data=image_data, filename=filename)


class ImageIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.request["ACTUAL_URL"] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name="Image")
        schema = fti.lookupSchema()
        self.assertTrue(schema.getName().endswith("_0_Image"))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name="Image")
        self.assertNotEqual(None, fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name="Image")
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(IImage.providedBy(new_object))

    def test_adding(self):
        self.portal.invokeFactory("Image", "doc1")
        self.assertTrue(IImage.providedBy(self.portal["doc1"]))


class ImageViewIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.request["ACTUAL_URL"] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.portal.invokeFactory("Image", "image")
        image = self.portal["image"]
        image.title = "My Image"
        image.description = "This is my image."
        image.image = dummy_image()
        self.image = image
        self.request.set("URL", image.absolute_url())
        self.request.set("ACTUAL_URL", image.absolute_url())
        alsoProvides(self.request, IPloneFormLayer)

    def test_image_view(self):
        view = self.image.restrictedTraverse("@@view")

        self.assertTrue(view())
        self.assertEqual(view.request.response.status, 200)
        self.assertTrue("My Image" in view())
        self.assertTrue("This is my image." in view())

    # XXX: Not working. See ImageFunctionalTest test_image_view_fullscreen
    # Problem seems to be that the image is not properly uploaded.
    #    def test_image_view_fullscreen(self):
    #        view = getMultiAdapter(
    #            (self.image, self.request),
    #            name='image_view_fullscreen'
    #        )
    #
    #        self.assertTrue(view())
    #        self.assertEqual(view.request.response.status, 200)
    #        self.assertTrue('image.jpg' in view())

    def test_svg_image(self):
        self.image.image = dummy_image("image.svg")
        scale = self.image.restrictedTraverse("@@images")
        self.assertRegex(
            scale.tag("image", scale="large"),
            r'<img src="http://nohost/plone/image/@@images/[a-z0-9\-]*.svg" alt="My Image" title="My Image" height="[a-z0-9\-]*" width="[a-z0-9\-]*" />',  # noqa: E501
        )


class ImageFunctionalTest(unittest.TestCase):

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

    def test_add_image(self):
        self.browser.open(self.portal_url)
        self.browser.getLink("Image").click()
        widget = "form.widgets.title"
        self.browser.getControl(name=widget).value = "My image"
        widget = "form.widgets.description"
        self.browser.getControl(name=widget).value = "This is my image."
        widget = "form.widgets.IShortName.id"
        self.browser.getControl(name=widget).value = "my-special-image.jpg"
        image_path = os.path.join(os.path.dirname(__file__), "image.jpg")
        image_ctl = self.browser.getControl(name="form.widgets.image")
        with io.FileIO(image_path, "rb") as f:
            image_ctl.add_file(f, "image/png", "image.jpg")
        self.browser.getControl("Save").click()
        self.assertTrue(self.browser.url.endswith("image.jpg/view"))
        self.assertIn("My image", self.browser.contents)
        self.assertIn("This is my image", self.browser.contents)
        self.assertIn("image.jpg", self.browser.contents)

    def test_add_image_with_shortname(self):
        self.browser.open(self.portal_url)
        self.browser.getLink("Image").click()
        widget = "form.widgets.title"
        self.browser.getControl(name=widget).value = "My image"
        widget = "form.widgets.IShortName.id"
        self.browser.getControl(name=widget).value = "my-special-image.jpg"
        image_path = os.path.join(os.path.dirname(__file__), "image.jpg")
        image_ctl = self.browser.getControl(name="form.widgets.image")
        with io.FileIO(image_path, "rb") as f:
            image_ctl.add_file(f, "image/png", "image.jpg")
        self.browser.getControl("Save").click()
        self.assertTrue(self.browser.url.endswith("my-special-image.jpg/view"))

    def test_image_view_fullscreen(self):
        self.browser.open(self.portal_url)
        self.browser.getLink("Image").click()
        self.assertTrue("Title" in self.browser.contents)
        self.assertTrue("Description" in self.browser.contents)
        self.assertTrue("Text" in self.browser.contents)
        widget = "form.widgets.title"
        self.browser.getControl(name=widget).value = "My image"
        widget = "form.widgets.description"
        self.browser.getControl(name=widget).value = "This is my image."
        image_path = os.path.join(os.path.dirname(__file__), "image.jpg")
        image_ctl = self.browser.getControl(name="form.widgets.image")
        with io.FileIO(image_path, "rb") as f:
            image_ctl.add_file(f, "image/png", "image.jpg")
        self.browser.getControl("Save").click()
        self.browser.getLink(url="/image_view_fullscreen").click()
        self.assertTrue(self.browser.url.endswith("image.jpg/image_view_fullscreen"))
        self.assertTrue("My image" in self.browser.contents)
        self.assertTrue("Back to site" in self.browser.contents)
