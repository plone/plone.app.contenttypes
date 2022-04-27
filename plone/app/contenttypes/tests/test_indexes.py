from plone.app.contenttypes.testing import (  # noqa
    PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING,
)
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.textfield.value import RichTextValue
from plone.rfc822.interfaces import IPrimaryFieldInfo
from Products.CMFCore.utils import getToolByName

import os
import unittest


class CatalogIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.portal.invokeFactory("Folder", "folder")
        self.folder = self.portal.folder
        self.folder.invokeFactory("Document", "document")
        self.folder.invokeFactory("News Item", "news_item")
        self.folder.invokeFactory("Link", "link")
        self.folder.invokeFactory("Image", "image")
        self.folder.invokeFactory("File", "file")
        self.folder.invokeFactory("Collection", "collection")
        self.folder.invokeFactory("Folder", "folder")
        self.document = self.folder.document
        self.news_item = self.folder.news_item
        self.link = self.folder.link
        self.image = self.folder.image
        self.file = self.folder.file
        self.collection = self.folder.collection
        # Note: this changes self.folder.
        self.folder = self.folder.folder
        self.catalog = getToolByName(self.portal, "portal_catalog")

    def test_id_in_searchable_text_index(self):
        brains = self.catalog.searchResults(
            dict(
                SearchableText="document",
            )
        )
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getPath(), "/plone/folder/document")

    def test_title_in_searchable_text_index(self):
        self.document.title = "My title"
        self.document.reindexObject()
        brains = self.catalog.searchResults(
            dict(
                SearchableText="My title",
            )
        )
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getPath(), "/plone/folder/document")

    def test_description_in_searchable_text_index(self):
        self.document.description = "My description"
        self.document.reindexObject()
        brains = self.catalog.searchResults(
            dict(
                SearchableText="My description",
            )
        )
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getPath(), "/plone/folder/document")

    def test_subject_in_searchable_text_index(self):
        self.document.setSubject(
            [
                "Apples",
                "Oranges",
            ]
        )
        self.document.reindexObject()
        brains = self.catalog.searchResults(
            dict(
                SearchableText="Apples",
            )
        )
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getPath(), "/plone/folder/document")

    def test_folder_fields_in_searchable_text_index(self):
        self.folder.title = "Carpeta"
        self.folder.description = "My description"
        self.folder.reindexObject()
        # Description
        brains = self.catalog.searchResults(
            dict(
                SearchableText="My description",
            )
        )
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getPath(), "/plone/folder/folder")
        # Title
        brains = self.catalog.searchResults(
            dict(
                SearchableText="Carpeta",
            )
        )
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getPath(), "/plone/folder/folder")

    def test_remote_url_in_searchable_text_index(self):
        self.link.remoteUrl = "http://www.plone.org/"
        self.link.reindexObject()
        brains = self.catalog.searchResults(
            dict(
                SearchableText="plone",
                portal_type="Link",
            )
        )
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getPath(), "/plone/folder/link")

    def test_text_in_searchable_text_index(self):
        self.document.text = RichTextValue("Lorem ipsum", "text/plain", "text/html")
        self.news_item.text = RichTextValue("Lorem ipsum", "text/plain", "text/html")
        self.collection.text = RichTextValue("Lorem ipsum", "text/plain", "text/html")
        self.document.reindexObject()
        self.news_item.reindexObject()
        self.collection.reindexObject()
        brains = self.catalog.searchResults(
            dict(
                SearchableText="Lorem ipsum",
            )
        )
        self.assertEqual(len(brains), 3)

        paths = [it.getPath() for it in brains]
        self.assertTrue("/plone/folder/news_item" in paths)
        self.assertTrue("/plone/folder/document" in paths)
        self.assertTrue("/plone/folder/collection" in paths)

    def test_html_stripped_searchable_text_index(self):
        """Ensure, html tags are stripped out from the content and not indexed."""
        self.document.text = RichTextValue(
            "<p>Lorem <b>ipsum</b></p>",
            mimeType="text/html",
            outputMimeType="text/html",
        )
        self.document.reindexObject()
        brains = self.catalog.searchResults(
            dict(
                SearchableText="Lorem ipsum",
            )
        )
        self.assertEqual(len(brains), 1)
        rid = brains[0].getRID()
        index_data = self.catalog.getIndexDataForRID(rid)
        self.assertEqual(index_data["SearchableText"].count("p"), 0)
        self.assertEqual(index_data["SearchableText"].count("b"), 0)

    def test_raw_text_searchable_text_index(self):
        """Ensure that raw text is used, instead of output.

        It makes no sense to transform raw text to the output mimetype,
        and then transform it again to plain text.
        Note that this does mean that javascript may get in the
        searchable text, but you will usually have a hard time setting it.
        """
        self.document.text = RichTextValue(
            """<script type="text/javascript">alert('Lorem ipsum')""" """</script>""",
            mimeType="text/html",
            outputMimeType="text/x-html-safe",
        )
        self.document.reindexObject()
        brains = self.catalog.searchResults(
            dict(
                SearchableText="Lorem ipsum",
            )
        )
        self.assertEqual(len(brains), 1)
        rid = brains[0].getRID()
        index_data = self.catalog.getIndexDataForRID(rid)
        self.assertEqual(index_data["SearchableText"].count("script"), 0)
        self.assertEqual(index_data["SearchableText"].count("text"), 0)

    def test_file_fulltext_in_searchable_text_plain(self):
        from plone.namedfile.file import NamedBlobFile

        data = "Lorem ipsum. Köln <!-- ...oder München, das ist hier die " "Frage. -->"
        test_file = NamedBlobFile(data=data, filename="string.txt")

        primary_field_info = IPrimaryFieldInfo(self.file)
        primary_field_info.field.set(self.file, test_file)
        self.file.reindexObject()

        brains = self.catalog.searchResults(dict(SearchableText="Lorem ipsum"))
        self.assertEqual(len(brains), 1)

        brains = self.catalog.searchResults(dict(SearchableText="Köln"))
        self.assertEqual(len(brains), 1)

        brains = self.catalog.searchResults(dict(SearchableText="München"))
        self.assertEqual(len(brains), 1)

    def test_file_fulltext_in_searchable_text_index_string(self):
        from plone.namedfile.file import NamedBlobFile

        data = "Lorem ipsum. Köln <!-- ...oder München, das ist hier die " "Frage. -->"
        test_file = NamedBlobFile(data=data, filename="string.html")

        primary_field_info = IPrimaryFieldInfo(self.file)
        primary_field_info.field.set(self.file, test_file)
        self.file.reindexObject()

        brains = self.catalog.searchResults(dict(SearchableText="Lorem ipsum"))
        self.assertEqual(len(brains), 1)

        brains = self.catalog.searchResults(dict(SearchableText="Köln"))
        self.assertEqual(len(brains), 1)

        brains = self.catalog.searchResults(dict(SearchableText="München"))
        self.assertEqual(len(brains), 0)  # hint: html comment is stripped

    def test_file_fulltext_in_searchable_text_index_unicode(self):
        from plone.namedfile.file import NamedBlobFile

        data = "Lorem ipsum Köln <!-- ...oder München, das ist hier die " "Frage. -->"
        test_file = NamedBlobFile(data=data, filename="unicode.html")

        primary_field_info = IPrimaryFieldInfo(self.file)
        primary_field_info.field.set(self.file, test_file)
        self.file.reindexObject()

        brains = self.catalog.searchResults(dict(SearchableText="Lorem ipsum"))
        self.assertEqual(len(brains), 1)

        brains = self.catalog.searchResults(dict(SearchableText="Köln"))
        self.assertEqual(len(brains), 1)

        brains = self.catalog.searchResults(dict(SearchableText="München"))
        self.assertEqual(len(brains), 0)  # hint: html comment is stripped

    def test_title_in_metadata(self):
        self.document.title = "My title"
        self.document.reindexObject()
        brains = self.catalog.searchResults(
            dict(
                path="/plone/folder/document",
            )
        )
        self.assertEqual(brains[0].Title, "My title")

    def test_description_in_metadata(self):
        self.document.description = "My description"
        self.document.reindexObject()
        brains = self.catalog.searchResults(
            dict(
                path="/plone/folder/document",
            )
        )
        self.assertEqual(brains[0].Description, "My description")

    def test_get_remote_url_in_metadata(self):
        self.link.remoteUrl = "http://www.plone.org/"
        self.link.reindexObject()
        brains = self.catalog.searchResults(
            dict(
                path="/plone/folder/link",
            )
        )
        self.assertEqual(brains[0].getRemoteUrl, "http://www.plone.org/")

    def test_get_remote_url_in_metadata_variables_replaced(self):
        """Link URL must be in catalog with the variables
        ${navigation_root_url} and ${portal_url} replaced by the corresponding
        paths. Otherwise the navigation portlet will show an wrong URL for the
        link object. (See issue #110)
        """
        self.link.remoteUrl = "${navigation_root_url}/my-item"
        self.link.reindexObject()
        brains = self.catalog.searchResults(
            dict(
                path="/plone/folder/link",
            )
        )
        self.assertEqual(brains[0].getRemoteUrl, "/plone/my-item")

    def test_getobjsize_image(self):
        from .test_image import dummy_image

        primary_field_info = IPrimaryFieldInfo(self.image)
        primary_field_info.field.set(self.image, dummy_image())
        self.image.reindexObject()

        brains = self.catalog.searchResults(
            dict(
                path="/plone/folder/image",
            )
        )

        self.assertEqual(
            "5.0 KB",
            brains[0].getObjSize,
        )

    def test_getobjsize_file(self):
        from plone.namedfile.file import NamedBlobFile

        filename = os.path.join(os.path.dirname(__file__), "image.jpg")
        with open(filename, "rb") as f:
            file_data = f.read()
        test_file = NamedBlobFile(data=file_data, filename=filename)

        primary_field_info = IPrimaryFieldInfo(self.file)
        primary_field_info.field.set(self.file, test_file)
        self.file.reindexObject()

        brains = self.catalog.searchResults(
            dict(
                path="/plone/folder/file",
            )
        )

        self.assertEqual(
            "5.0 KB",
            brains[0].getObjSize,
        )
