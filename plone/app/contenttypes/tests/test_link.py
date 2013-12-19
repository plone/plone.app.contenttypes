# -*- coding: utf-8 -*-
import unittest2 as unittest

from zope.interface import alsoProvides
from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser

from plone.app.contenttypes.interfaces import ILink

from plone.app.contenttypes.testing import (
    PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING,
    PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING
)

from plone.app.testing import TEST_USER_ID, setRoles
from plone.app.z3cform.interfaces import IPloneFormLayer


class LinkIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_schema(self):
        fti = queryUtility(
            IDexterityFTI,
            name='Link')
        schema = fti.lookupSchema()
        self.assertEqual(schema.getName(), 'plone_0_Link')

    def test_fti(self):
        fti = queryUtility(
            IDexterityFTI,
            name='Link'
        )
        self.assertNotEquals(None, fti)

    def test_factory(self):
        fti = queryUtility(
            IDexterityFTI,
            name='Link'
        )
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(ILink.providedBy(new_object))

    def test_adding(self):
        self.portal.invokeFactory(
            'Link',
            'doc1'
        )
        self.assertTrue(ILink.providedBy(self.portal['doc1']))


class LinkViewIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Link', 'link')
        link = self.portal['link']
        link.title = "My Link"
        link.description = "This is my link."
        self.link = link
        self.request.set('URL', link.absolute_url())
        self.request.set('ACTUAL_URL', link.absolute_url())
        alsoProvides(self.request, IPloneFormLayer)

    def test_link_redirect_view(self):
        view = self.link.restrictedTraverse('@@view')
        self.assertTrue(view())
        self.assertEqual(view.request.response.status, 200)
        self.assertTrue('My Link' in view())
        self.assertTrue('This is my link.' in view())

    # XXX: ToDo: We have to write tests to properly test the
    # link_redirect_view. It seems such tests never existed in
    # ATContentTypes.


class LinkFunctionalTest(unittest.TestCase):

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

    def test_add_link(self):
        self.browser.open(self.portal_url)
        self.browser.getLink('Link').click()
        self.browser.getControl(name='form.widgets.IDublinCore.title')\
            .value = "My link"
        self.browser.getControl(name='form.widgets.IDublinCore.description')\
            .value = "This is my link."
        self.browser.getControl('Save').click()

        self.assertTrue(self.browser.url.endswith('my-link/view'))
        self.assertTrue('My link' in self.browser.contents)
        self.assertTrue('This is my link' in self.browser.contents)
