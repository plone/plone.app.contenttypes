# -*- coding: utf-8 -*-
import os
import unittest2 as unittest

from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser

from plone.app.contenttypes.testing import (
    PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING
)

from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer
from zope.interface import alsoProvides

from plone.dexterity.fti import DexterityFTI

from plone.app.testing import TEST_USER_ID, setRoles


class LeadImageBehaviorFunctionalTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = DexterityFTI('leadimagefolder')
        self.portal.portal_types._setObject('leadimagefolder', fti)
        fti.klass = 'plone.dexterity.content.Container'
        fti.behaviors = (
            'plone.app.contenttypes.behaviors.leadimage.ILeadImage',
        )
        self.fti = fti
        alsoProvides(self.portal.REQUEST, IPloneAppContenttypesLayer)
        alsoProvides(self.request, IPloneAppContenttypesLayer)
        from plone.app.contenttypes.behaviors.leadimage import ILeadImage
        alsoProvides(self.request, ILeadImage)
        self.portal.invokeFactory(
            'leadimagefolder',
            id='leadimagefolder',
            title=u'Folder with a lead image'
        )
        import transaction
        transaction.commit()
        # Set up browser
        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def test_lead_image_in_edit_form(self):
        self.browser.open(self.portal_url + '/leadimagefolder/edit')
        self.assertTrue('Lead Image' in self.browser.contents)
        self.assertTrue('Lead Image Caption' in self.browser.contents)

    def test_lead_image_viewlet_shows_up(self):
        self.browser.open(self.portal_url + '/leadimagefolder/edit')
        # Image upload
        file_path = os.path.join(os.path.dirname(__file__), "image.jpg")
        file_ctl = self.browser.getControl(
            name='form.widgets.ILeadImage.image'
        )
        file_ctl.add_file(open(file_path), 'image/png', 'image.jpg')
        # Image caption
        self.browser.getControl(
            name='form.widgets.ILeadImage.image_caption'
        ).value = 'My image caption'
        # Submit form
        self.browser.getControl('Save').click()

        self.assertTrue('My image caption' in self.browser.contents)
        self.assertTrue('image.jpg' in self.browser.contents)

        self.assertTrue('<div class="leadImage">' in self.browser.contents)

        # But doesn't show up on folder_contents, which is not a default view
        self.browser.open(self.portal_url + '/leadimagefolder/folder_contents')
        self.assertTrue('<div class="leadImage">' not in self.browser.contents)
