# -*- coding: utf-8 -*-
import json
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


class CollectionBehaviorFunctionalTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        fti = DexterityFTI('collectioncontainer')
        self.portal.portal_types._setObject('collectioncontainer', fti)
        fti.klass = 'plone.dexterity.content.Container'
        fti.behaviors = (
            'plone.app.contenttypes.behaviors.collection.ICollection',
        )
        self.fti = fti
        alsoProvides(self.portal.REQUEST, IPloneAppContenttypesLayer)
        alsoProvides(self.request, IPloneAppContenttypesLayer)
        from plone.app.contenttypes.behaviors.collection import ICollection
        alsoProvides(self.request, ICollection)
        self.portal.invokeFactory(
            'collectioncontainer',
            id='collectioncontainer',
            title=u'Container with a collection',
            customViewFields=['Title', 'portal_type'],
            query=query,
        )
        self.portal.invokeFactory(
            'Document',
            id='doc',
            title=u'Collection Test Page',
        )

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

    def test_collection_default_dexterity_view(self):
        # Test the default dexterity view
        browser = self._get_browser()
        browser.open(self.portal_url + '/collectioncontainer/view')
        self.assertTrue('"v": "Collection Test Page"' in browser.contents)

    def test_collection_tabular_view(self):
        browser = self._get_browser()
        browser.open(self.portal_url + '/collectioncontainer/tabular_view')
        # search from here:
        start = browser.contents.find('content-core')
        # The test string should be within the search results.
        self.assertTrue('Collection Test Page' in
                        browser.contents[start:start + 1000])

    def test_collection_in_edit_form(self):
        browser = self._get_browser()
        browser.open(self.portal_url + '/collectioncontainer/edit')
        control = browser.getControl(name='form.widgets.ICollection.query')
        self.assertTrue(json.loads(control.value)[0]['v'],
                        'Collection Test Page')
        # The customViewFields field is a 'double' control, with a
        # 'from' and 'to' list.
        from_control = browser.getControl(
            name='form.widgets.ICollection.customViewFields.from')
        self.assertEqual(from_control.value, [])
        self.assertTrue('Title' not in from_control.options)
        self.assertTrue('portal_type' not in from_control.options)
        self.assertTrue('Description' in from_control.options)
