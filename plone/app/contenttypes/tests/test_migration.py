# -*- coding: utf-8 -*-
import unittest2 as unittest

from Products.CMFCore.utils import getToolByName

from zope.interface import directlyProvides

from plone.dexterity.fti import DexterityFTI

from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer

from plone.app.contenttypes.interfaces import (
    IDocument,
    IEvent,
    IFile,
    IFolder,
    IImage,
    ILink,
    INewsItem,
)

from plone.app.contenttypes.testing import \
    PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

from plone.app.testing import TEST_USER_ID, setRoles


class FixBaseclassesTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        self.request['URL'] = self.portal.absolute_url()
        directlyProvides(self.request, IPloneAppContenttypesLayer)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.catalog = getToolByName(self.portal, "portal_catalog")
        fti = DexterityFTI('mockobject')
        fti.klass = 'plone.dexterity.content.Item'
        self.portal.portal_types._setObject('mockobject', fti)
        self.portal.invokeFactory('mockobject', 'obj1')
        self.obj = self.portal.obj1

    def test_view_is_registered(self):
        view = self.portal.restrictedTraverse('fix_base_classes')
        self.assertIsInstance(view(), str)

    def test_fix_interface_for_document(self):
        self.obj.portal_type = 'Document'
        self.catalog.reindexObject(self.obj)

        self.portal.restrictedTraverse('fix_base_classes')()

        self.assertTrue(IDocument.providedBy(self.obj))

    def test_fix_interface_for_event(self):
        self.obj.portal_type = 'Event'
        self.catalog.reindexObject(self.obj)

        self.portal.restrictedTraverse('fix_base_classes')()

        self.assertTrue(IEvent.providedBy(self.obj))

    def test_fix_interface_for_file(self):
        self.obj.portal_type = 'File'
        self.catalog.reindexObject(self.obj)

        self.portal.restrictedTraverse('fix_base_classes')()

        self.assertTrue(IFile.providedBy(self.obj))

    def test_fix_interface_for_folder(self):
        self.obj.portal_type = 'Folder'
        self.catalog.reindexObject(self.obj)

        self.portal.restrictedTraverse('fix_base_classes')()

        self.assertTrue(IFolder.providedBy(self.obj))

    def test_fix_interface_for_image(self):
        self.obj.portal_type = 'Image'
        self.catalog.reindexObject(self.obj)

        self.portal.restrictedTraverse('fix_base_classes')()

        self.assertTrue(IImage.providedBy(self.obj))

    def test_fix_interface_for_link(self):
        self.obj.portal_type = 'Link'
        self.catalog.reindexObject(self.obj)

        self.portal.restrictedTraverse('fix_base_classes')()

        self.assertTrue(ILink.providedBy(self.obj))

    def test_fix_interface_for_news_item(self):
        self.obj.portal_type = 'News Item'
        self.catalog.reindexObject(self.obj)

        self.portal.restrictedTraverse('fix_base_classes')()

        self.assertTrue(INewsItem.providedBy(self.obj))


class MigrateToATContentTypesTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        self.request['URL'] = self.portal.absolute_url()
        directlyProvides(self.request, IPloneAppContenttypesLayer)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.catalog = getToolByName(self.portal, "portal_catalog")

    def createATCTobject(self, klass, id):
        '''Borrowed from ATCTFieldTestCase'''
        import transaction
        portal = self.portal
        obj = klass(oid=id)
        obj = obj.__of__(portal)
        portal[id] = obj
        obj.initializeArchetype()
        transaction.savepoint()
        return obj

    def get_migrator(self, obj, migrator_class):
        src_portal_type = migrator_class.src_portal_type
        dst_portal_type = migrator_class.dst_portal_type
        migrator = migrator_class(obj, src_portal_type=src_portal_type,
                                  dst_portal_type=dst_portal_type)
        return migrator

    def test_new_content_is_indexed(self):
        from Products.ATContentTypes.content.document import ATDocument
        from plone.app.contenttypes.browser.migration import DocumentMigrator
        from plone.app.contenttypes.interfaces import IDocument
        at_document = self.createATCTobject(ATDocument, 'document')
        migrator = self.get_migrator(at_document, DocumentMigrator)
        migrator.migrate()
        brains = self.catalog(object_provides=IDocument.__identifier__)
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getObject(), self.portal['document'])

    def test_old_content_is_removed(self):
        from Products.ATContentTypes.content.document import ATDocument
        from plone.app.contenttypes.browser.migration import DocumentMigrator
        at_document = self.createATCTobject(ATDocument, 'document')
        migrator = self.get_migrator(at_document, DocumentMigrator)
        migrator.migrate()
        brains = self.catalog(portal_type='Document')
        self.assertEqual(len(brains), 1)

    def test_document_is_migrated(self):
        from Products.ATContentTypes.content.document import ATDocument
        from plone.app.contenttypes.browser.migration import DocumentMigrator
        from plone.app.contenttypes.interfaces import IDocument
        at_document = self.createATCTobject(ATDocument, 'document')
        migrator = self.get_migrator(at_document, DocumentMigrator)
        migrator.migrate()
        new_document = self.portal['document']
        self.assertTrue(IDocument.providedBy(new_document))
        self.assertTrue(at_document is not new_document)
