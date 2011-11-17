from Acquisition import aq_base
import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from plone.app.contenttypes.testing import \
    PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

from plone.app.testing import TEST_USER_ID, setRoles


class News_itemTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])        

    def test_schema(self):
        fti = queryUtility(IDexterityFTI,
                           name='News Item')
        schema = fti.lookupSchema()
         
        self.assertEquals(schema.__module__,
                          'plone.dexterity.schema.generated')
        self.assertEquals(schema.__name__,
                          'plone_0_News_1_Item')

    def test_fti(self):
        fti = queryUtility(IDexterityFTI,
                           name='News Item')
        
        self.assertNotEquals(None, fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI,
                           name='News Item')
        factory = fti.factory
        news_item = createObject(factory)
        
        self.assertEquals(str(type(news_item)),
                          "<class 'plone.dexterity.content.Item'>")

    def test_adding(self):
        self.portal.invokeFactory('News Item',
                                  'news_item')
        news_item = self.portal['news_item']
        
        self.assertEquals(str(type(aq_base(news_item))),
                          "<class 'plone.dexterity.content.Item'>")

    def test_view(self):
        self.portal.invokeFactory('News Item', 'news_item')
        news_item = self.portal['news_item']
        self.request.set('URL', news_item.absolute_url())
        self.request.set('ACTUAL_URL', news_item.absolute_url())        
        view = news_item.restrictedTraverse('@@view')

        self.failUnless(view())
        self.assertEquals(view.request.response.status, 200)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
