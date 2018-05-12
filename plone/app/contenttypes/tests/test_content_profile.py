# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletManager
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from Products.PythonScripts.PythonScript import PythonScript
from zope.component import getMultiAdapter
from zope.component import getUtility

import pkg_resources
import unittest


try:
    pkg_resources.get_distribution('plone.app.dexterity.behaviors.constraints')
except pkg_resources.DistributionNotFound:
    DEXTERITY_WITH_CONSTRAINS = False
else:
    DEXTERITY_WITH_CONSTRAINS = True


class PloneAppContenttypesContent(PloneSandboxLayer):
    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpPloneSite(self, portal):
        # Necessary to set up some Plone stuff, such as Workflow.
        self.applyProfile(portal, 'plone.app.contenttypes:plone-content')


PLONE_APP_CONTENTTYPES_CONTENT_FIXTURE = PloneAppContenttypesContent()
PLONE_APP_CONTENTTYPES_CONTENT_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(PLONE_APP_CONTENTTYPES_CONTENT_FIXTURE,),
                       name='PloneAppContenttypesContent:Integration')

# TODO Test for content translation.


class ContentProfileTestCase(unittest.TestCase):
    layer = PLONE_APP_CONTENTTYPES_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal_workflow = getToolByName(self.portal, 'portal_workflow')

    # #################### #
    #   front-page tests   #
    # #################### #

    def test_frontpage_was_created(self):
        # Was the object created?
        obj = self.portal['front-page']
        self.assertEqual(obj.portal_type, 'Document')

    def test_frontpage_is_default_page(self):
        # Has the object been set on the container as the default page?
        self.assertEqual(self.portal.default_page, 'front-page')

    def test_frontpage_is_published(self):
        # Has the content object been published?
        front_page = self.portal['front-page']
        current_state = self.portal_workflow.getInfoFor(
            front_page,
            'review_state')
        self.assertEqual(current_state, 'published')

    # ################# #
    #   Members tests   #
    # ################# #

    def test_Members_was_created(self):
        # Was the object created?
        obj = self.portal['Members']
        self.assertEqual(obj.portal_type, 'Folder')

    @unittest.skip('Replaced by new members-search-form')
    def test_Members__index_html(self):
        # Was the index_html script created?
        obj = self.portal['Members']['index_html']
        self.assertTrue(isinstance(obj, PythonScript))
        # It's outside the scope of this test to verify the contents of
        # the script are correct. Simply checking for existence should
        # be enough.

    def test_Members_portlets(self):
        # Have the right column portlet manager setting been added?
        members = self.portal['Members']
        manager = getUtility(IPortletManager, name='plone.rightcolumn')
        assignable_manager = getMultiAdapter((members, manager),
                                             ILocalPortletAssignmentManager)
        self.assertTrue(assignable_manager.getBlacklistStatus('context'))
        self.assertTrue(assignable_manager.getBlacklistStatus('group'))
        self.assertTrue(assignable_manager.getBlacklistStatus('content_type'))

    def test_Members_is_private(self):
        # Is the content object public?
        obj = self.portal['Members']
        current_state = self.portal_workflow.getInfoFor(obj, 'review_state')
        self.assertEqual(current_state, 'private')

    # ################ #
    #   events tests   #
    # ################ #

    def test_events_was_created(self):
        # Was the object created?
        events = self.portal['events']
        self.assertEqual(events.portal_type, 'Folder')
        # Was the contained collection created?
        collection = events['aggregator']
        self.assertEqual(collection.portal_type, 'Collection')

    def test_events_default_page(self):
        # Has the object been set on the container as the default page?
        self.assertEqual(self.portal['events'].default_page, 'aggregator')

    def test_events_is_published(self):
        # Has the content object been published?
        events = self.portal['events']
        current_state = self.portal_workflow.getInfoFor(events, 'review_state')
        self.assertEqual(current_state, 'published')

    @unittest.skipUnless(
        DEXTERITY_WITH_CONSTRAINS,
        'Dexterity constraints are not present')
    def test_events_allowable_types(self):
        events = self.portal['events']
        behavior = ISelectableConstrainTypes(events)
        types = ['Event']
        self.assertEqual(types, behavior.getImmediatelyAddableTypes())

    # ############## #
    #   news tests   #
    # ############## #

    def test_news_was_created(self):
        # Was the object created?
        news = self.portal['news']
        self.assertEqual(news.portal_type, 'Folder')
        # Was the contained collection created?
        collection = news['aggregator']
        self.assertEqual(collection.portal_type, 'Collection')

    def test_news_default_page(self):
        # Has the object been set on the container as the default page?
        self.assertEqual(self.portal['news'].default_page, 'aggregator')

    def test_news_is_published(self):
        # Has the content object been published?
        news = self.portal['news']
        current_state = self.portal_workflow.getInfoFor(news, 'review_state')
        self.assertEqual(current_state, 'published')

    @unittest.skipUnless(
        DEXTERITY_WITH_CONSTRAINS,
        'Dexterity constraints are not present')
    def test_news_allowable_types(self):
        news = self.portal['news']
        behavior = ISelectableConstrainTypes(news)
        types = ['News Item']
        self.assertEqual(types, behavior.getImmediatelyAddableTypes())

    def test_news_aggregator_settings(self):
        # Has the news aggregator (Collection) been set up?
        query = [dict(i=u'portal_type',
                      o=u'plone.app.querystring.operation.selection.any',
                      v=[u'News Item']),
                 dict(i=u'review_state',
                      o=u'plone.app.querystring.operation.selection.any',
                      v=[u'published']),
                 ]
        collection = self.portal['news']['aggregator']
        self.assertEqual(collection.sort_on, u'effective')
        self.assertEqual(collection.sort_reversed, True)
        self.assertEqual(collection.query, query)
        self.assertEqual(collection.getLayout(), 'summary_view')
