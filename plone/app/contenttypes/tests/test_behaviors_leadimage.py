# -*- coding: utf-8 -*-
import unittest2 as unittest

from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser

from plone.app.contenttypes.testing import (
    PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING,
    PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING
)

from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer
from zope.interface import alsoProvides

from plone.dexterity.fti import DexterityFTI

from plone.app.testing import TEST_USER_ID, setRoles


class DocumentFunctionalText(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        fti = DexterityFTI('leadimagedocument')
        self.portal.portal_types._setObject('leadimagedocument', fti)
        fti.klass = 'plone.dexterity.content.Item'
        fti.behaviors = ('plone.app.contenttypes.behaviors.leadimage.ILeadImage',)
        alsoProvides(self.portal.REQUEST, IPloneAppContenttypesLayer)
        alsoProvides(self.request, IPloneAppContenttypesLayer)
        self.portal.invokeFactory(
            'leadimagedocument',
            id='leadimagedoc',
            title=u'Document with a lead image'
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
        self.browser.open(self.portal_url + '/leadimagedoc/edit')
        self.assertTrue('Lead Image' in self.browser.contents)
        self.assertTrue('Lead Image Caption' in self.browser.contents)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
