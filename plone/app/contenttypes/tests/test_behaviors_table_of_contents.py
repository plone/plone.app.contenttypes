from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer
from plone.app.contenttypes.testing import (  # noqa
    PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING,
)
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.fti import DexterityFTI
from plone.testing.zope import Browser
from zope.interface import alsoProvides

import unittest


class TableOfContentsBehaviorFunctionalTest(unittest.TestCase):
    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        fti = DexterityFTI("tocdocument")
        self.portal.portal_types._setObject("tocdocument", fti)
        fti.klass = "plone.dexterity.content.Item"
        fti.behaviors = ("plone.tableofcontents", "plone.richtext")
        self.fti = fti
        alsoProvides(self.request, IPloneAppContenttypesLayer)
        self.portal.invokeFactory(
            "tocdocument", id="tocdoc", title="Document with a table of contents",
        )
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

    def test_toc_in_edit_form(self):
        self.browser.open(self.portal_url + "/tocdoc/edit")
        self.assertTrue("Table of contents" in self.browser.contents)

    def test_toc_viewlet_shows_up(self):
        self.browser.open(self.portal_url + "/tocdoc/edit")
        toc_ctl = self.browser.getControl(
            name="form.widgets.ITableOfContents.table_of_contents:list"
        )
        toc_ctl.value = [
            "selected",
        ]
        # Submit form
        self.browser.getControl("Save").click()
        self.assertTrue('id="document-toc"' in self.browser.contents)
