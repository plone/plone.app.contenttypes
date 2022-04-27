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

import io
import os
import unittest


class LeadImageBehaviorFunctionalTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        fti = DexterityFTI("leadimagefolder")
        self.portal.portal_types._setObject("leadimagefolder", fti)
        fti.klass = "plone.dexterity.content.Container"
        fti.behaviors = (
            "plone.app.contenttypes.behaviors.leadimage.ILeadImageBehavior",
        )
        self.fti = fti
        alsoProvides(self.portal.REQUEST, IPloneAppContenttypesLayer)
        alsoProvides(self.request, IPloneAppContenttypesLayer)
        from plone.app.contenttypes.behaviors.leadimage import ILeadImage

        alsoProvides(self.request, ILeadImage)
        self.portal.invokeFactory(
            "leadimagefolder", id="leadimagefolder", title="Folder with a lead image"
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

    def test_lead_image_in_edit_form(self):
        self.browser.open(self.portal_url + "/leadimagefolder/edit")
        self.assertTrue("Lead Image" in self.browser.contents)
        self.assertTrue("Lead Image Caption" in self.browser.contents)

    def test_lead_image_viewlet_shows_up(self):
        self.browser.open(self.portal_url + "/leadimagefolder/edit")
        # Image upload
        file_path = os.path.join(os.path.dirname(__file__), "image.jpg")
        file_ctl = self.browser.getControl(name="form.widgets.ILeadImageBehavior.image")
        with io.FileIO(file_path, "rb") as f:
            file_ctl.add_file(f, "image/png", "image.jpg")
        # Image caption
        self.browser.getControl(
            name="form.widgets.ILeadImageBehavior.image_caption"
        ).value = "My image caption"
        # Submit form
        self.browser.getControl("Save").click()

        self.assertTrue("My image caption" in self.browser.contents)
        self.assertTrue("image.jpg" in self.browser.contents)

        self.assertTrue('<section id="section-leadimage">' in self.browser.contents)

        # But doesn't show up on folder_contents, which is not a default view
        self.browser.open(self.portal_url + "/leadimagefolder/folder_contents")
        self.assertTrue('<section id="section-leadimage">' not in self.browser.contents)
