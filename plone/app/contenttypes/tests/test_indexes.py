# -*- coding: utf-8 -*-
import unittest2 as unittest

from Products.CMFCore.utils import getToolByName

from plone.app.textfield.value import RichTextValue

from plone.app.contenttypes.testing import (
    PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING
)

from plone.app.testing import TEST_USER_ID, setRoles


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
        self.document = self.folder.document
        self.news_item = self.folder.news_item
        self.link = self.folder.link
        self.catalog = getToolByName(self.portal, 'portal_catalog')

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
        
