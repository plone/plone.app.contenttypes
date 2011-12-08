# -*- coding: utf-8 -*-
import unittest2 as unittest
from Products.CMFCore.utils import getToolByName
from plone.app.testing import PloneSandboxLayer, IntegrationTesting
from plone.app.contenttypes.testing import \
    PLONE_APP_CONTENTTYPES_FIXTURE


class PloneAppContenttypesContent(PloneSandboxLayer):
    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpPloneSite(self, portal):
        # Necessary to set up some Plone stuff, such as Workflow.
        self.applyProfile(portal, 'Products.CMFPlone:plone')
        self.applyProfile(portal, 'plone.app.contenttypes:plone-content')

PLONE_APP_CONTENTTYPES_CONTENT_FIXTURE = PloneAppContenttypesContent()
PLONE_APP_CONTENTTYPES_CONTENT_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(PLONE_APP_CONTENTTYPES_CONTENT_FIXTURE,),
                       name="PloneAppContenttypesContent:Integration")

# TODO Test for content translation.


class ContentProfileTestCase(unittest.TestCase):
    layer = PLONE_APP_CONTENTTYPES_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

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

    def test_frontpage_is_in_presentation_mode(self):
        # Has presentation mode been set?
        
        # NOTE Presentation mode is built into ATDocument and things like
        #      plone.app.layout simply take advantage of its capabilities.
        self.fail("The implementation for presentation mode is missing.")

    def test_frontpage_is_published(self):
        # Has the content object been published?
        front_page = self.portal['front-page']
        portal_workflow = getToolByName(self.portal, 'portal_workflow')
        current_state = portal_workflow.getInfoFor(front_page, 'review_state')
        self.assertEqual(current_state, 'published')
