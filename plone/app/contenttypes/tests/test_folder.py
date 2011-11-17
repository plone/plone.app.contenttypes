from Acquisition import aq_base
import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from plone.app.contenttypes.testing import \
    PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

from plone.app.testing import TEST_USER_ID, setRoles


class FolderTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])        

    def test_schema(self):
        fti = queryUtility(IDexterityFTI,
                           name='Folder')
        schema = fti.lookupSchema()
         
        self.assertEquals(schema.__module__,
                          'plone.dexterity.schema.generated')
        self.assertEquals(schema.__name__,
                          'plone_0_Folder')

    def test_fti(self):
        fti = queryUtility(IDexterityFTI,
                           name='Folder')
        
        self.assertNotEquals(None, fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI,
                           name='Folder')
        factory = fti.factory
        folder = createObject(factory)
        
        self.assertEquals(str(type(folder)),
                          "<class 'plone.dexterity.content.Container'>")

    def test_adding(self):
        self.portal.invokeFactory('Folder',
                                  'folder')
        folder = self.portal['folder']
        
        self.assertEquals(str(type(aq_base(folder))),
                          "<class 'plone.dexterity.content.Container'>")

    def test_view(self):
        self.portal.invokeFactory('Folder', 'folder')
        folder = self.portal['folder']
        self.request.set('URL', folder.absolute_url())
        self.request.set('ACTUAL_URL', folder.absolute_url())        
        view = folder.restrictedTraverse('@@view')

        self.failUnless(view())
        self.assertEquals(view.request.response.status, 200)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
