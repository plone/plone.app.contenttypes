from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.base.interfaces.constrains import ISelectableConstrainTypes
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletManager
from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.PythonScript import PythonScript
from zope.component import getMultiAdapter
from zope.component import getUtility

import unittest


class PloneAppContenttypesContent(PloneSandboxLayer):
    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpPloneSite(self, portal):
        # Necessary to set up some Plone stuff, such as Workflow.
        self.applyProfile(portal, "plone.app.contenttypes:plone-content")


PLONE_APP_CONTENTTYPES_CONTENT_FIXTURE = PloneAppContenttypesContent()
PLONE_APP_CONTENTTYPES_CONTENT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_CONTENTTYPES_CONTENT_FIXTURE,),
    name="PloneAppContenttypesContent:Integration",
)

# TODO Test for content translation.


class ContentProfileTestCase(unittest.TestCase):
    layer = PLONE_APP_CONTENTTYPES_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.portal_workflow = getToolByName(self.portal, "portal_workflow")

    # #################### #
    #   front-page tests   #
    # #################### #

    def test_homepage(self):
        self.assertEqual(self.portal.title, "Welcome to Plone")
        self.assertEqual(
            self.portal.description,
            "Congratulations! You have successfully installed Plone.",
        )
        self.assertIn("Welcome!", self.portal.text.raw)

    # ################# #
    #   Members tests   #
    # ################# #

    def test_Members_was_created(self):
        # Was the object created?
        obj = self.portal["Members"]
        self.assertEqual(obj.portal_type, "Folder")

    def test_Members_portlets(self):
        # Have the right column portlet manager setting been added?
        members = self.portal["Members"]
        manager = getUtility(IPortletManager, name="plone.rightcolumn")
        assignable_manager = getMultiAdapter(
            (members, manager), ILocalPortletAssignmentManager
        )
        self.assertTrue(assignable_manager.getBlacklistStatus("context"))
        self.assertTrue(assignable_manager.getBlacklistStatus("group"))
        self.assertTrue(assignable_manager.getBlacklistStatus("content_type"))

    def test_Members_is_private(self):
        # Is the content object public?
        obj = self.portal["Members"]
        current_state = self.portal_workflow.getInfoFor(obj, "review_state")
        self.assertEqual(current_state, "private")

    # ################ #
    #   events tests   #
    # ################ #

    def test_events_was_created(self):
        # Was the object created?
        events = self.portal["events"]
        self.assertEqual(events.portal_type, "Folder")
        # Was the contained collection created?
        collection = events["aggregator"]
        self.assertEqual(collection.portal_type, "Collection")

    def test_events_default_page(self):
        # Has the object been set on the container as the default page?
        self.assertEqual(self.portal["events"].default_page, "aggregator")

    def test_events_is_published(self):
        # Has the content object been published?
        events = self.portal["events"]
        current_state = self.portal_workflow.getInfoFor(events, "review_state")
        self.assertEqual(current_state, "published")

    # ############## #
    #   news tests   #
    # ############## #

    def test_news_was_created(self):
        # Was the object created?
        news = self.portal["news"]
        self.assertEqual(news.portal_type, "Folder")
        # Was the contained collection created?
        collection = news["aggregator"]
        self.assertEqual(collection.portal_type, "Collection")

    def test_news_default_page(self):
        # Has the object been set on the container as the default page?
        self.assertEqual(self.portal["news"].default_page, "aggregator")

    def test_news_is_published(self):
        # Has the content object been published?
        news = self.portal["news"]
        current_state = self.portal_workflow.getInfoFor(news, "review_state")
        self.assertEqual(current_state, "published")

    def test_news_aggregator_settings(self):
        # Has the news aggregator (Collection) been set up?
        query = [
            dict(
                i="portal_type",
                o="plone.app.querystring.operation.selection.any",
                v=["News Item"],
            ),
            dict(
                i="review_state",
                o="plone.app.querystring.operation.selection.any",
                v=["published"],
            ),
        ]
        collection = self.portal["news"]["aggregator"]
        self.assertEqual(collection.sort_on, "effective")
        self.assertEqual(collection.sort_reversed, True)
        self.assertEqual(collection.query, query)
        self.assertEqual(collection.getLayout(), "summary_view")
