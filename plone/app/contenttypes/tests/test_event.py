# -*- coding: utf-8 -*-
from datetime import datetime
from plone.app.contenttypes.testing import (
    PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING,
    PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING
)
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID, setRoles
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.dexterity.interfaces import IDexterityFTI
from plone.event.interfaces import IEvent
from plone.testing.z2 import Browser
from zope.component import createObject
from zope.component import queryUtility
from zope.interface import alsoProvides

import unittest2 as unittest


class EventIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        self.request['LANGUAGE'] = 'en'
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_schema(self):
        fti = queryUtility(
            IDexterityFTI,
            name='Event')
        schema = fti.lookupSchema()
        self.assertEqual(schema.getName(), 'plone_0_Event')

    def test_fti(self):
        fti = queryUtility(
            IDexterityFTI,
            name='Event'
        )
        self.assertNotEquals(None, fti)

    def test_factory(self):
        fti = queryUtility(
            IDexterityFTI,
            name='Event'
        )
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IEvent.providedBy(new_object))

    def test_adding(self):
        self.portal.invokeFactory(
            'Event',
            'doc1'
        )
        self.assertTrue(IEvent.providedBy(self.portal['doc1']))

    def test_view(self):
        self.portal.invokeFactory('Event', 'event')
        event = self.portal['event']
        event.title = "My Event"
        event.description = "This is my event."
        event.start = datetime(2013, 1, 1, 10, 0)
        event.end = datetime(2013, 1, 1, 12, 0)

        self.request.set('URL', event.absolute_url())
        self.request.set('ACTUAL_URL', event.absolute_url())
        alsoProvides(self.request, IPloneFormLayer)
        view = event.restrictedTraverse('@@view')

        # TODO: start/end are not set??
        #
        self.assertTrue(view())
        self.assertEquals(view.request.response.status, 200)
        self.assertTrue('My Event' in view())
        self.assertTrue('This is my event.' in view())


class EventFunctionalTest(unittest.TestCase):

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

    def test_add_event(self):
        self.browser.open(self.portal_url)
        self.browser.getLink('Event').click()
        self.browser.getControl(
            name='form.widgets.IDublinCore.title'
        ).value = "My event"
        self.browser.getControl(
            name='form.widgets.IDublinCore.description'
        ).value = "This is my event."
        self.browser.getControl(
            name='form.widgets.IEventSummary.text'
        ).value = "Lorem Ipsum"
        self.browser.getControl(
            name='form.widgets.IEventBasic.start-day'
        ).value = ['1']
        self.browser.getControl(
            name='form.widgets.IEventBasic.start-month'
        ).value = ['1']
        self.browser.getControl(
            name='form.widgets.IEventBasic.start-year'
        ).value = ['2013']
        self.browser.getControl(
            name='form.widgets.IEventBasic.end-day'
        ).value = ['12']
        self.browser.getControl(
            name='form.widgets.IEventBasic.end-month'
        ).value = ['1']
        self.browser.getControl(
            name='form.widgets.IEventBasic.end-year'
        ).value = ['2013']
        self.browser.getControl('Save').click()

        self.assertTrue(self.browser.url.endswith('my-event/view'))
        self.assertTrue('My event' in self.browser.contents)
        self.assertTrue('This is my event' in self.browser.contents)
        self.assertTrue('Lorem Ipsum' in self.browser.contents)
        self.assertTrue('2013-01-01' in self.browser.contents)
        self.assertTrue('2013-01-12' in self.browser.contents)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
