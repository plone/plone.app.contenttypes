# -*- coding: utf-8 -*-
import unittest2 as unittest

from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from plone.app.testing import TEST_USER_ID, setRoles

from plone.app.contenttypes.testing import (
    PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING
)

from plone.app.contenttypes.upgrades import update_fti
from plone.app.contenttypes.upgrades import migrate_to_folderish_types
from plone.app.contenttypes.content import Document


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


class UpgradeTo1103IntegrationTest(unittest.TestCase):
    """Test the upgrade to folderish types
    """

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])


    def test_migrate_to_folderish_types(self):
        fti = queryUtility(
            IDexterityFTI,
            name='Document'
        )
        fti.klass = "plone.app.contenttypes.tests.oldtypes.Document"

        self.portal.invokeFactory(
            'Folder',
            'folder1'
        )
        folder1 = self.portal['folder1']
        folder1.invokeFactory(
            'Document',
            'doc1'
        )
        folder1.invokeFactory(
            'News Item',
            'news1'
        )
        doc1 = folder1['doc1']
        doc1.description = "A initially itemish Document"
        news1 = folder1['news1']
        self.assertEqual(doc1.meta_type, 'Dexterity Item')
        self.assertEqual(news1.meta_type, 'Dexterity Container')
        # We can't change the base_class of the document class in a test
        # while keeping the class the same. So we fake this by changing the
        # class of the instance and re-adding it to the folder.
        folder1._delOb('doc1')
        doc1.__class__ = Document
        folder1._setOb('doc1', doc1)
        # Setting the fti to the default is not really needed for the test
        # but is closer to the real thing where obj.__class__ and fti.klass
        # stay the same. Also this would allow us to use
        # migrate_base_class_to_new_class(obj, migrate_to_folderish=True)
        # in the upgrade-step.
        fti.klass = "plone.app.contenttypes.content.Document"

        migrate_to_folderish_types(self.portal.portal_setup)
        self.assertEqual(doc1.meta_type, 'Dexterity Container')
        view = doc1.restrictedTraverse('@@view')()
        self.assertIn('A initially itemish Document', view)
