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


class TableOfContentsBehaviorFunctionalTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = DexterityFTI('tocdocument')
        self.portal.portal_types._setObject('tocdocument', fti)
        fti.klass = 'plone.dexterity.content.Item'
        fti.behaviors = (
            'plone.app.contenttypes.behaviors.tableofcontents.'
            'ITableOfContents',
        )
        self.fti = fti
        alsoProvides(self.portal.REQUEST, IPloneAppContenttypesLayer)
        alsoProvides(self.request, IPloneAppContenttypesLayer)
        from plone.app.contenttypes.behaviors.tableofcontents \
            import ITableOfContents
        alsoProvides(self.request, ITableOfContents)
        self.portal.invokeFactory(
            'tocdocument',
            id='tocdoc',
            title=u'Document with a table of contents'
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

    def test_toc_in_edit_form(self):
        self.browser.open(self.portal_url + '/tocdoc/edit')
        self.assertTrue('Table of contents' in self.browser.contents)

    def test_toc_viewlet_shows_up(self):
        self.browser.open(self.portal_url + '/tocdoc/edit')
        toc_ctl = self.browser.getControl(
            name='form.widgets.ITableOfContents.table_of_contents:list'
        )
        toc_ctl.value = [u"selected"]
        # Submit form
        self.browser.getControl('Save').click()
        self.assertTrue('<section id="document-toc"' in self.browser.contents)
