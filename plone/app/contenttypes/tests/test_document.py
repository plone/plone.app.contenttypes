# -*- coding: utf-8 -*-
from Acquisition import aq_base
import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser

from plone.app.contenttypes.testing import (
    PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING,
    PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING
)

from plone.app.testing import TEST_USER_ID, setRoles


class DocumentIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_schema(self):
        fti = queryUtility(IDexterityFTI,
                           name='Document')
        schema = fti.lookupSchema()
        self.assertEquals(schema.__module__,
                          'plone.dexterity.schema.generated')
        self.assertEquals(schema.__name__,
                          'plone_0_Document')

    def test_fti(self):
        fti = queryUtility(IDexterityFTI,
                           name='Document')

        self.assertNotEquals(None, fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI,
                           name='Document')
        factory = fti.factory
        document = createObject(factory)

        self.assertEquals(str(type(document)),
                          "<class 'plone.dexterity.content.Item'>")

    def test_adding(self):
        self.portal.invokeFactory('Document',
                                  'document')
        document = self.portal['document']

        self.assertEquals(str(type(aq_base(document))),
                          "<class 'plone.dexterity.content.Item'>")

    def test_view(self):
        self.portal.invokeFactory('Document', 'document')
        document = self.portal['document']
        self.request.set('URL', document.absolute_url())
        self.request.set('ACTUAL_URL', document.absolute_url())
        view = document.restrictedTraverse('@@view')

        self.failUnless(view())
        self.assertEquals(view.request.response.status, 200)


class DocumentFunctionalText(unittest.TestCase):

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

    def test_add_document(self):
        self.browser.open(self.portal_url)
        self.browser.getLink('Page').click()
        self.assertTrue('Title' in self.browser.contents)
        self.assertTrue('Description' in self.browser.contents)
        self.assertTrue('Text' in self.browser.contents)
        self.browser.getControl(name='form.widgets.IDublinCore.title')\
        .value = "My document"
        self.browser.getControl(name='form.widgets.IDublinCore.description')\
        .value = "This is my document."
        self.browser.getControl(name='form.widgets.text')\
        .value = "Lorem Ipsum"
        self.browser.getControl('Save').click()
        self.assertTrue(self.browser.url.endswith('my-document/view'))
        self.assertTrue('My document' in self.browser.contents)
        self.assertTrue('This is my document' in self.browser.contents)
        self.assertTrue('Lorem Ipsum' in self.browser.contents)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
