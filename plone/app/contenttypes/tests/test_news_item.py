# -*- coding: utf-8 -*-
import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from plone.app.textfield.value import RichTextValue

from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser

from plone.app.contenttypes.interfaces import INewsItem

from plone.app.contenttypes.testing import (
    PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING,
    PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING
)

from plone.app.testing import TEST_USER_ID, setRoles


class NewsItemIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_schema(self):
        fti = queryUtility(
            IDexterityFTI,
            name='News Item')
        schema = fti.lookupSchema()
        self.assertEqual(schema.getName(), 'plone_0_News_1_Item')

    def test_fti(self):
        fti = queryUtility(
            IDexterityFTI,
            name='News Item'
        )
        self.assertNotEquals(None, fti)

    def test_factory(self):
        fti = queryUtility(
            IDexterityFTI,
            name='News Item'
        )
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(INewsItem.providedBy(new_object))

    def test_adding(self):
        self.portal.invokeFactory(
            'News Item',
            'doc1'
        )
        self.assertTrue(INewsItem.providedBy(self.portal['doc1']))

    def test_view(self):
        self.portal.invokeFactory('News Item', 'news_item')
        news_item = self.portal['news_item']
        news_item.title = "My News Item"
        news_item.description = "This is my news item."
        news_item.text = RichTextValue(
            u"Lorem ipsum",
            'text/plain',
            'text/html'
        )
        self.request.set('URL', news_item.absolute_url())
        self.request.set('ACTUAL_URL', news_item.absolute_url())
        view = news_item.restrictedTraverse('@@view')

        self.assertTrue(view())
        self.assertEquals(view.request.response.status, 200)
        self.assertTrue('My News Item' in view())
        self.assertTrue('This is my news item.' in view())
        self.assertTrue('Lorem ipsum' in view())


class NewsItemFunctionalText(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

#    def test_add_news_item(self):
#        self.browser.open(self.portal_url)
#        self.browser.getLink('News Item').click()
#        self.assertTrue('Title' in self.browser.contents)
#        self.assertTrue('Description' in self.browser.contents)
#        self.assertTrue('Text' in self.browser.contents)
#        self.browser.getControl(name='form.widgets.IDublinCore.title')\
#            .value = "My news item"
#        self.browser.getControl(name='form.widgets.IDublinCore.description')\
#            .value = "This is my news item."
#        self.browser.getControl(name='form.widgets.text')\
#            .value = "Lorem Ipsum"
#        self.browser.getControl('Save').click()
#        self.assertTrue(self.browser.url.endswith('my-news-item/view'))
#        self.assertTrue('My news item' in self.browser.contents)
#        self.assertTrue('This is my news item' in self.browser.contents)
#        self.assertTrue('Lorem Ipsum' in self.browser.contents)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
