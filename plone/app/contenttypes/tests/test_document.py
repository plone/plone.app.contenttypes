import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from plone.app.contenttypes.testing import \
    PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

from plone.app.testing import TEST_USER_ID, setRoles

from plone.app.contenttypes.interfaces import IPage


class PloneAppContenttypesTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_schema(self):
        fti = queryUtility(IDexterityFTI,
                           name='page')
        schema = fti.lookupSchema()
        self.assertEquals(IPage, schema)

    def test_fti(self):
        fti = queryUtility(IDexterityFTI,
                           name='page')
        self.assertNotEquals(None, fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI,
                           name='page')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IPage.providedBy(new_object))

    def test_adding(self):
        self.invokeFactory('page',
                                  'page1')
        p1 = self['page1']
        self.failUnless(IPage.providedBy(p1))

    def test_view(self):
        self.invokeFactory('page', 'page1')
        p1 = self['page']
        view = p1.restrictedTraverse('@@view')
        self.failUnless(view)
        self.assertEquals(view.request.response.status, 200)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
