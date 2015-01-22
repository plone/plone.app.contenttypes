# -*- coding: utf-8 -*-
import unittest2 as unittest

from plone.app.contenttypes.testing import \
    PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

from plone.app.testing import TEST_USER_ID, setRoles


class PloneAppContenttypesSetupTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.types = self.portal.portal_types

    def test_old_topic_disabled(self):
        self.assertTrue('Topic' not in self.types.objectIds())

    def test_atcontenttypes_replaced_by_dexterity_types(self):
        self.assertEqual(self.types['Collection'].meta_type, 'Dexterity FTI')
        self.assertEqual(self.types['Document'].meta_type, 'Dexterity FTI')
        self.assertEqual(self.types['Event'].meta_type, 'Dexterity FTI')
        self.assertEqual(self.types['File'].meta_type, 'Dexterity FTI')
        self.assertEqual(self.types['Folder'].meta_type, 'Dexterity FTI')
        self.assertEqual(self.types['Image'].meta_type, 'Dexterity FTI')
        self.assertEqual(self.types['Link'].meta_type, 'Dexterity FTI')
        self.assertEqual(self.types['News Item'].meta_type, 'Dexterity FTI')

    def test_browserlayer_available(self):
        from plone.browserlayer import utils
        from plone.app.contenttypes.interfaces import \
            IPloneAppContenttypesLayer
        self.assertTrue(
            IPloneAppContenttypesLayer in utils.registered_layers()
        )

    def test_css_registered(self):
        resreg = getattr(self.portal, 'portal_registry')
        from Products.CMFPlone.interfaces import IResourceRegistry
        resources_ids = resreg.collectionOfInterface(
            IResourceRegistry, prefix="plone.resources").keys()
        self.assertTrue(
            'resource-collection-css' in resources_ids)
