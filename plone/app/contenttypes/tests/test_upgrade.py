# -*- coding: utf-8 -*-
import unittest2 as unittest

from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from plone.app.testing import TEST_USER_ID, setRoles

from plone.app.contenttypes.testing import (
    PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING
)

from plone.app.contenttypes.upgrades import update_fti
from plone.app.contenttypes.upgrades import use_new_view_names


class UpgradeTo1000IntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_update_fti_document(self):
        fti = queryUtility(
            IDexterityFTI,
            name='Document'
        )
        fti.model_file = 'plone.app.contenttypes:document.xml'

        update_fti(self.portal)

        fti = queryUtility(
            IDexterityFTI,
            name='Document'
        )
        self.assertEqual(
            fti.model_file,
            'plone.app.contenttypes.schema:document.xml'
        )

    def test_update_fti_file(self):
        fti = queryUtility(
            IDexterityFTI,
            name='File'
        )
        fti.model_file = 'plone.app.contenttypes:file.xml'

        update_fti(self.portal)

        fti = queryUtility(
            IDexterityFTI,
            name='File'
        )
        self.assertEqual(
            fti.model_file,
            'plone.app.contenttypes.schema:file.xml'
        )

    def test_update_fti_folder(self):
        fti = queryUtility(
            IDexterityFTI,
            name='Folder'
        )
        fti.model_file = 'plone.app.contenttypes:folder.xml'

        update_fti(self.portal)

        fti = queryUtility(
            IDexterityFTI,
            name='Folder'
        )
        self.assertEqual(
            fti.model_file,
            'plone.app.contenttypes.schema:folder.xml'
        )

    def test_update_fti_image(self):
        fti = queryUtility(
            IDexterityFTI,
            name='File'
        )
        fti.model_file = 'plone.app.contenttypes:image.xml'

        update_fti(self.portal)

        fti = queryUtility(
            IDexterityFTI,
            name='File'
        )
        self.assertEqual(
            fti.model_file,
            'plone.app.contenttypes.schema:file.xml'
        )

    def test_update_fti_link(self):
        fti = queryUtility(
            IDexterityFTI,
            name='Link'
        )
        fti.model_file = 'plone.app.contenttypes:link.xml'

        update_fti(self.portal)

        fti = queryUtility(
            IDexterityFTI,
            name='Link'
        )
        self.assertEqual(
            fti.model_file,
            'plone.app.contenttypes.schema:link.xml'
        )

    def test_update_fti_news_item(self):
        fti = queryUtility(
            IDexterityFTI,
            name='News Item'
        )
        fti.model_file = 'plone.app.contenttypes:news_item.xml'

        update_fti(self.portal)

        fti = queryUtility(
            IDexterityFTI,
            name='News Item'
        )
        self.assertEqual(
            fti.model_file,
            'plone.app.contenttypes.schema:news_item.xml'
        )

    def test_use_new_view_names(self):
        old_methods = (
            'atct_album_view',
            'folder_summary_view',
            'folder_tabular_view',
            'folder_listing',
        )

        new_methods = (
            'listing_view',
            'summary_view',
            'tabular_view',
            'full_view',
            'album_view',
            'event_listing'
        )

        self.portal.invokeFactory('Folder', 'folder1')
        folder = self.portal['folder1']
        folder.setLayout('folder_summary_view')
        folder_fti = queryUtility(IDexterityFTI, name='Folder')
        folder_fti.manage_changeProperties(
            view_methods=old_methods,
            default_view='folder_summary_view',
        )

        portal_fti = self.portal.portal_types.get('Plone Site')
        portal_fti.manage_changeProperties(
            view_methods=old_methods,
            default_view='folder_listing',
        )
        self.portal.setLayout('folder_tabular_view')
        self.portal.setDefaultPage('folder1')

        self.assertEqual(folder_fti.view_methods, old_methods)
        self.assertEqual(folder_fti.default_view, 'folder_summary_view')

        self.assertEqual(portal_fti.view_methods, old_methods)
        self.assertEqual(portal_fti.default_view, 'folder_listing')

        # run upgrade-step
        use_new_view_names(self.portal, types_to_fix=['Folder', 'Plone Site'])

        self.assertEqual(folder_fti.view_methods, new_methods)
        self.assertEqual(folder_fti.default_view, 'summary_view')
        self.assertEqual(folder.getLayout(), 'summary_view')

        self.assertEqual(self.portal.getLayout(), 'tabular_view')
        self.assertEqual(self.portal.getDefaultPage(), 'folder1')
        self.assertEqual(portal_fti.default_view, 'listing_view')
        self.assertEqual(portal_fti.view_methods, new_methods)
