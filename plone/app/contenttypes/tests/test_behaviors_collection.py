# -*- coding: utf-8 -*-
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

query = [{
    'i': 'Title',
    'o': 'plone.app.querystring.operation.string.contains',
    'v': 'Collection Test Page',
}]


class DocumentFunctionalTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        fti = DexterityFTI('collectiondocument')
        self.portal.portal_types._setObject('collectiondocument', fti)
        fti.klass = 'plone.dexterity.content.Item'
        fti.behaviors = (
            'plone.app.contenttypes.behaviors.collection.ICollection',
        )
        self.fti = fti
        alsoProvides(self.portal.REQUEST, IPloneAppContenttypesLayer)
        alsoProvides(self.request, IPloneAppContenttypesLayer)
        from plone.app.contenttypes.behaviors.collection import ICollection
        alsoProvides(self.request, ICollection)
        self.portal.invokeFactory(
            'collectiondocument',
            id='collectiondoc',
            title=u'Document with a collection',
        )
        self.portal.collectiondoc.query=query

    def _get_browser(self):
        # Need to commit transaction, otherwise the browser does not
        # see anything.
        import transaction
        transaction.commit()
        # Set up browser
        app = self.layer['app']
        browser = Browser(app)
        browser.handleErrors = False
        browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )
        return browser

    def test_collection_in_edit_form(self):
        browser = self._get_browser()
        browser.open(self.portal_url + '/collectiondoc/edit')
        self.assertTrue('Query' in browser.contents)
        control = browser.getControl(
            name='form.widgets.ICollection.query.v:records')
        self.assertTrue(control.value, 'Collection Test Page')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
