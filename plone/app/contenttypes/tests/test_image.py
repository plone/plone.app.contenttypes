from Acquisition import aq_base
import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from plone.app.contenttypes.testing import \
    PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

from plone.app.testing import TEST_USER_ID, setRoles


class ImageTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])        

    def test_schema(self):
        fti = queryUtility(IDexterityFTI,
                           name='Image')
        schema = fti.lookupSchema()
         
        self.assertEquals(schema.__module__,
                          'plone.dexterity.schema.generated')
        self.assertEquals(schema.__name__,
                          'plone_0_Image')

    def test_fti(self):
        fti = queryUtility(IDexterityFTI,
                           name='Image')
        
        self.assertNotEquals(None, fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI,
                           name='Image')
        factory = fti.factory
        image = createObject(factory)
        
        self.assertEquals(str(type(image)),
                          "<class 'plone.dexterity.content.Item'>")

    def test_adding(self):
        self.portal.invokeFactory('Image',
                                  'image')
        image = self.portal['image']
        
        self.assertEquals(str(type(aq_base(image))),
                          "<class 'plone.dexterity.content.Item'>")

    def test_view(self):
        self.portal.invokeFactory('Image', 'image')
        image = self.portal['image']
        self.request.set('URL', image.absolute_url())
        self.request.set('ACTUAL_URL', image.absolute_url())        
        view = image.restrictedTraverse('@@view')

        self.failUnless(view())
        self.assertEquals(view.request.response.status, 200)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
