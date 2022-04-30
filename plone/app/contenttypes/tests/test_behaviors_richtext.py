from plone.app.contenttypes.behaviors.richtext import IRichText
from plone.app.contenttypes.testing import (  # noqa
    PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING,
)
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.fti import DexterityFTI
from plone.testing.zope import Browser
from Products.CMFCore.utils import getToolByName

import unittest


class RichTextBase:
    # subclass here
    _behaviors = None
    _portal_type = None

    def _setupFTI(self):
        fti = DexterityFTI(self._portal_type)
        self.portal.portal_types._setObject(self._portal_type, fti)
        fti.klass = "plone.dexterity.content.Item"
        fti.behaviors = self._behaviors


class RichTextBehaviorFunctionalTest(RichTextBase, unittest.TestCase):
    """basic use cases and tests for richtext behavior"""

    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    _behaviors = ("plone.app.contenttypes.behaviors.richtext.IRichTextBehavior",)
    _portal_type = "SomeDocument"

    def setUp(self):
        app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.wf = getToolByName(self.portal, "portal_workflow")
        self.portal.acl_users._doAddUser("user_std", "secret", ["Member"], [])
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self._setupFTI()
        self.portal.invokeFactory(self._portal_type, "doc1")
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        import transaction

        transaction.commit()
        # Set up browser
        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization",
            "Basic {}:{}".format(
                SITE_OWNER_NAME,
                SITE_OWNER_PASSWORD,
            ),
        )

    def test_richtext_in_edit_form(self):
        self.browser.open(self.portal_url + "/doc1/edit")
        self.assertTrue("tinymce" in self.browser.contents)

    def test_richtext_behavior(self):
        IRichText.providedBy(self.portal.doc1)
