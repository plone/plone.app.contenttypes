from Acquisition import aq_base
import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

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
        self.assertEquals(self.types['Document'].meta_type, 'Dexterity FTI')
        self.assertEquals(self.types['Event'].meta_type, 'Dexterity FTI')
        self.assertEquals(self.types['File'].meta_type, 'Dexterity FTI')
        self.assertEquals(self.types['Folder'].meta_type, 'Dexterity FTI')
        self.assertEquals(self.types['Image'].meta_type, 'Dexterity FTI')
        self.assertEquals(self.types['Link'].meta_type, 'Dexterity FTI')
        self.assertEquals(self.types['News Item'].meta_type, 'Dexterity FTI')

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
