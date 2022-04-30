from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer
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
from plone.namedfile.file import NamedFile
from plone.testing.zope import Browser
from zope.component import createObject
from zope.component import queryUtility
from zope.interface import alsoProvides

import io
import os.path
import transaction
import unittest


class FileIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.request["ACTUAL_URL"] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name="File")
        schema = fti.lookupSchema()
        self.assertTrue(schema.getName().endswith("_0_File"))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name="File")
        self.assertNotEqual(None, fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name="File")
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(IFile.providedBy(new_object))

    def test_adding(self):
        self.portal.invokeFactory("File", "doc1")
        self.assertTrue(IFile.providedBy(self.portal["doc1"]))

    def test_view(self):
        self.portal.invokeFactory("File", "file")
        file1 = self.portal["file"]
        file1.title = "My File"
        file1.description = "This is my file."
        self.request.set("URL", file1.absolute_url())
        self.request.set("ACTUAL_URL", file1.absolute_url())
        alsoProvides(self.request, IPloneFormLayer)
        view = file1.restrictedTraverse("@@view")

        self.assertTrue(view())
        self.assertEqual(view.request.response.status, 200)
        self.assertTrue("My File" in view())
        self.assertTrue("This is my file." in view())

    def test_view_no_video_audio_tag(self):
        self.portal.invokeFactory("File", "file")
        file = self.portal["file"]
        file.file = NamedFile()
        file.file.contentType = "application/pdf"
        alsoProvides(self.request, IPloneAppContenttypesLayer)
        view = file.restrictedTraverse("@@file_view")
        rendered = view()
        self.assertTrue("</audio>" not in rendered)
        self.assertTrue("</video>" not in rendered)

    def test_view_video_tag(self):
        self.portal.invokeFactory("File", "file")
        file = self.portal["file"]
        file.file = NamedFile()
        file.file.contentType = "audio/mp3"
        alsoProvides(self.request, IPloneAppContenttypesLayer)
        view = file.restrictedTraverse("@@file_view")
        rendered = view()
        self.assertTrue("</audio>" in rendered)

    def test_view_audio_tag(self):
        self.portal.invokeFactory("File", "file")
        file = self.portal["file"]
        file.file = NamedFile()
        file.file.contentType = "video/ogv"
        alsoProvides(self.request, IPloneAppContenttypesLayer)
        view = file.restrictedTraverse("@@file_view")
        rendered = view()
        self.assertTrue("</video>" in rendered)


class FileFunctionalTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        self.icons = self.portal.restrictedTraverse("@@iconresolver")
        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization",
            "Basic {}:{}".format(
                SITE_OWNER_NAME,
                SITE_OWNER_PASSWORD,
            ),
        )

    def test_add_file(self):
        self.browser.open(self.portal_url)
        self.browser.getLink("File").click()
        widget = "form.widgets.title"
        self.browser.getControl(name=widget).value = "My file"
        widget = "form.widgets.description"
        self.browser.getControl(name=widget).value = "This is my file."
        file_path = os.path.join(os.path.dirname(__file__), "image.jpg")
        file_ctl = self.browser.getControl(name="form.widgets.file")
        with io.FileIO(file_path, "rb") as f:
            file_ctl.add_file(f, "image/png", "image.jpg")
        self.browser.getControl("Save").click()
        self.assertTrue(self.browser.url.endswith("image.jpg/view"))
        self.assertTrue("My file" in self.browser.contents)
        self.assertTrue("This is my file" in self.browser.contents)

    def test_shortname_file(self):
        self.browser.open(self.portal_url)
        self.browser.getLink("File").click()
        widget = "form.widgets.title"
        self.browser.getControl(name=widget).value = "My file"
        widget = "form.widgets.IShortName.id"
        self.browser.getControl(name=widget).value = "my-special-file"
        file_path = os.path.join(os.path.dirname(__file__), "image.jpg")
        file_ctl = self.browser.getControl(name="form.widgets.file")
        with io.FileIO(file_path, "rb") as f:
            file_ctl.add_file(f, "image/png", "image.jpg")
        self.browser.getControl("Save").click()
        self.assertTrue(self.browser.url.endswith("my-special-file/view"))

    def test_mime_icon_pdf_for_file_(self):
        self.browser.open(self.portal_url)
        self.browser.getLink("File").click()

        widget = "form.widgets.title"
        self.browser.getControl(name=widget).value = "My file"
        widget = "form.widgets.description"
        self.browser.getControl(name=widget).value = "This is my pdf file."
        file_path = os.path.join(os.path.dirname(__file__), "file.pdf")
        file_ctl = self.browser.getControl(name="form.widgets.file")
        with io.FileIO(file_path, "rb") as f:
            file_ctl.add_file(f, "application/pdf", "file.pdf")
        self.browser.getControl("Save").click()
        self.assertTrue(self.browser.url.endswith("file.pdf/view"))
        # check icon
        self.assertEqual(
            "http://nohost/plone/++plone++bootstrap-icons/file-earmark-pdf.svg",
            self._get_icon_url(self.portal["file.pdf"].file.contentType),
        )

    def test_alternative_mime_icon_doc_for_file(self):
        mtr = self.portal.mimetypes_registry
        mime_doc = mtr.lookup("application/msword")[0]
        mime_doc.icon_path = "custom.png"
        transaction.commit()
        self.browser.open(self.portal_url)
        self.browser.getLink("File").click()

        widget = "form.widgets.title"
        self.browser.getControl(name=widget).value = "My file"
        widget = "form.widgets.description"
        self.browser.getControl(name=widget).value = "This is my doc file."
        file_path = os.path.join(os.path.dirname(__file__), "file.doc")
        file_ctl = self.browser.getControl(name="form.widgets.file")
        with io.FileIO(file_path, "rb") as f:
            file_ctl.add_file(f, "application/msword", "file.doc")
        self.browser.getControl("Save").click()
        self.assertTrue(self.browser.url.endswith("file.doc/view"))
        # check icon
        self.assertEqual(
            "http://nohost/plone/++plone++bootstrap-icons/file-earmark-richtext.svg",
            self._get_icon_url(self.portal["file.doc"].file.contentType),
        )

    def test_mime_icon_odt_for_file_(self):
        self.browser.open(self.portal_url)
        self.browser.getLink("File").click()

        widget = "form.widgets.title"
        self.browser.getControl(name=widget).value = "My file"
        widget = "form.widgets.description"
        self.browser.getControl(name=widget).value = "This is my odt file."
        file_path = os.path.join(os.path.dirname(__file__), "file.odt")
        file_ctl = self.browser.getControl(name="form.widgets.file")
        with io.FileIO(file_path, "rb") as f:
            file_ctl.add_file(f, "application/vnd.oasis.opendocument.text", "file.odt")
        self.browser.getControl("Save").click()
        self.assertTrue(self.browser.url.endswith("file.odt/view"))
        # check icon
        self.assertEqual(
            "http://nohost/plone/++plone++bootstrap-icons/file-earmark-richtext.svg",
            self._get_icon_url(self.portal["file.odt"].file.contentType),
        )

    def _get_icon_url(self, mime_type):
        return self.icons.url("mimetype-" + mime_type)
