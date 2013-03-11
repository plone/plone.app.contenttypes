# -*- coding: utf-8 -*-
import os
import unittest2 as unittest

from Products.CMFCore.utils import getToolByName

from plone.app.textfield.value import RichTextValue

from plone.app.contenttypes.testing import (
    PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING
)

from plone.app.testing import TEST_USER_ID, setRoles
from plone.rfc822.interfaces import IPrimaryFieldInfo


class CatalogIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'folder')
        self.folder = self.portal.folder
        self.folder.invokeFactory(
            'Document',
            'document'
        )
        self.folder.invokeFactory(
            'News Item',
            'news_item'
        )
        self.folder.invokeFactory(
            'Link',
            'link'
        )
        self.folder.invokeFactory(
            'Image',
            'image'
        )
        self.folder.invokeFactory(
            'File',
            'file'
        )
        self.document = self.folder.document
        self.news_item = self.folder.news_item
        self.link = self.folder.link
        self.image = self.folder.image
        self.file = self.folder.file
        self.catalog = getToolByName(self.portal, 'portal_catalog')

    def test_id_in_searchable_text_index(self):
        brains = self.catalog.searchResults(dict(
            SearchableText="document",
        ))
        self.assertEqual(len(brains), 1)
        self.assertEquals(
            brains[0].getPath(),
            '/plone/folder/document'
        )

    def test_title_in_searchable_text_index(self):
        self.document.title = "My title"
        self.document.reindexObject()
        brains = self.catalog.searchResults(dict(
            SearchableText="My title",
        ))
        self.assertEqual(len(brains), 1)
        self.assertEquals(
            brains[0].getPath(),
            '/plone/folder/document'
        )

    def test_description_in_searchable_text_index(self):
        self.document.description = "My description"
        self.document.reindexObject()
        brains = self.catalog.searchResults(dict(
            SearchableText="My description",
        ))
        self.assertEqual(len(brains), 1)
        self.assertEquals(
            brains[0].getPath(),
            '/plone/folder/document'
        )

    def test_remote_url_in_searchable_text_index(self):
        self.link.remoteUrl = 'http://www.plone.org/'
        self.link.reindexObject()
        brains = self.catalog.searchResults(dict(
            SearchableText="plone",
        ))
        self.assertEqual(len(brains), 1)
        self.assertEquals(
            brains[0].getPath(),
            '/plone/folder/link'
        )

    def test_text_in_searchable_text_index(self):
        self.document.text = RichTextValue(
            u'Lorem ipsum',
            'text/plain',
            'text/html'
        )
        self.news_item.text = RichTextValue(
            u'Lorem ipsum',
            'text/plain',
            'text/html'
        )
        self.document.reindexObject()
        self.news_item.reindexObject()
        brains = self.catalog.searchResults(dict(
            SearchableText=u'Lorem ipsum',
        ))
        self.assertEqual(len(brains), 2)
        self.assertEquals(
            brains[0].getPath(),
            '/plone/folder/news_item'
        )
        self.assertEquals(
            brains[1].getPath(),
            '/plone/folder/document'
        )

    def test_title_in_metadata(self):
        self.document.title = "My title"
        self.document.reindexObject()
        brains = self.catalog.searchResults(dict(
            path="/plone/folder/document",
        ))
        self.assertEquals(
            brains[0].Title,
            "My title"
        )

    def test_description_in_metadata(self):
        self.document.description = "My description"
        self.document.reindexObject()
        brains = self.catalog.searchResults(dict(
            path="/plone/folder/document",
        ))
        self.assertEquals(
            brains[0].Description,
            "My description"
        )

    def test_get_remote_url_in_metadata(self):
        self.link.remoteUrl = 'http://www.plone.org/'
        self.link.reindexObject()
        brains = self.catalog.searchResults(dict(
            path="/plone/folder/link",
        ))
        self.assertEquals(
            brains[0].getRemoteUrl,
            "http://www.plone.org/"
        )

    def test_getobjsize_image(self):
        from .test_image import dummy_image

        primary_field_info = IPrimaryFieldInfo(self.image)
        primary_field_info.field.set(self.image, dummy_image())
        self.image.reindexObject()

        brains = self.catalog.searchResults(dict(
            path="/plone/folder/image",
        ))

        # XXX: Do we still rely on getObjSize in portal_skins/plone_scripts?
        self.assertEquals(
            self.portal.getObjSize(None, primary_field_info.value.size),
            brains[0].getObjSize,
        )

    def test_getobjsize_file(self):
        from plone.namedfile.file import NamedBlobFile

        filename = os.path.join(os.path.dirname(__file__), u'image.jpg')
        test_file = NamedBlobFile(data=open(filename, 'r').read(),
                                  filename=filename)

        primary_field_info = IPrimaryFieldInfo(self.file)
        primary_field_info.field.set(self.file, test_file)
        self.file.reindexObject()

        brains = self.catalog.searchResults(dict(
            path="/plone/folder/file",
        ))

        # XXX: Do we still rely on getObjSize in portal_skins/plone_scripts?
        self.assertEquals(
            self.portal.getObjSize(None, primary_field_info.value.size),
            brains[0].getObjSize,
        )

