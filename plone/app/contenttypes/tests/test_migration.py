# -*- coding: utf-8 -*-
import os.path
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

    def get_test_image_data(self):
        test_image_path = os.path.join(os.path.dirname(__file__), 'image.png')
        with open(test_image_path, 'rb') as test_image_file:
            test_image_data = test_image_file.read()
        return test_image_data

    def get_migrator(self, obj, migrator_class):
        src_portal_type = migrator_class.src_portal_type
        dst_portal_type = migrator_class.dst_portal_type
        migrator = migrator_class(obj, src_portal_type=src_portal_type,
                                  dst_portal_type=dst_portal_type)
        return migrator

    def test_new_content_is_indexed(self):
        from Products.ATContentTypes.content.document import ATDocument
        from plone.app.contenttypes.migration import DocumentMigrator
        from plone.app.contenttypes.interfaces import IDocument
        at_document = self.createATCTobject(ATDocument, 'document')
        migrator = self.get_migrator(at_document, DocumentMigrator)
        migrator.migrate()
        brains = self.catalog(object_provides=IDocument.__identifier__)
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getObject(), self.portal['document'])

    def test_old_content_is_removed(self):
        from Products.ATContentTypes.content.document import ATDocument
        from plone.app.contenttypes.migration import DocumentMigrator
        at_document = self.createATCTobject(ATDocument, 'document')
        migrator = self.get_migrator(at_document, DocumentMigrator)
        migrator.migrate()
        brains = self.catalog(portal_type='Document')
        self.assertEqual(len(brains), 1)

    def test_old_content_is_unindexed(self):
        from Products.ATContentTypes.content.document import ATDocument
        from Products.ATContentTypes.interfaces import IATDocument
        from plone.app.contenttypes.migration import DocumentMigrator
        at_document = self.createATCTobject(ATDocument, 'document')
        migrator = self.get_migrator(at_document, DocumentMigrator)
        brains = self.catalog(object_provides=IATDocument.__identifier__)
        self.assertEqual(len(brains), 1)
        migrator.migrate()
        brains = self.catalog(object_provides=IATDocument.__identifier__)
        self.assertEqual(len(brains), 0)

    def test_document_is_migrated(self):
        from Products.ATContentTypes.content.document import ATDocument
        from plone.app.contenttypes.migration import DocumentMigrator
        from plone.app.contenttypes.interfaces import IDocument
        at_document = self.createATCTobject(ATDocument, 'document')
        migrator = self.get_migrator(at_document, DocumentMigrator)
        migrator.migrate()
        new_document = self.portal['document']
        self.assertTrue(IDocument.providedBy(new_document))
        self.assertTrue(at_document is not new_document)

    def test_file_is_migrated(self):
        from Products.ATContentTypes.content.file import ATFile
        from plone.app.contenttypes.migration import FileMigrator
        from plone.app.contenttypes.interfaces import IFile
        at_file = self.createATCTobject(ATFile, 'file')
        migrator = self.get_migrator(at_file, FileMigrator)
        migrator.migrate()
        new_file = self.portal['file']
        self.assertTrue(IFile.providedBy(new_file))
        self.assertTrue(at_file is not new_file)

    def test_file_content_is_migrated(self):
        from plone.app.contenttypes.migration import FileMigrator
        from plone.namedfile.interfaces import INamedFile
        from Products.ATContentTypes.content.file import ATFile
        at_file = self.createATCTobject(ATFile, 'file')
        field = at_file.getField('file')
        field.set(at_file, 'dummydata')
        field.setFilename(at_file, 'dummyfile.txt')
        field.setContentType(at_file, 'text/dummy')
        migrator = self.get_migrator(at_file, FileMigrator)
        migrator.migrate()
        new_file = self.portal['file']
        self.assertTrue(INamedFile.providedBy(new_file.file))
        self.assertEqual(new_file.file.filename, 'dummyfile.txt')
        self.assertEqual(new_file.file.contentType, 'text/dummy')
        self.assertEqual(new_file.file.data, 'dummydata')

    def test_image_is_migrated(self):
        from Products.ATContentTypes.content.image import ATImage
        from plone.app.contenttypes.migration import ImageMigrator
        from plone.app.contenttypes.interfaces import IImage
        at_image = self.createATCTobject(ATImage, 'image')
        migrator = self.get_migrator(at_image, ImageMigrator)
        migrator.migrate()
        new_image = self.portal['image']
        self.assertTrue(IImage.providedBy(new_image))
        self.assertTrue(at_image is not new_image)

    def test_empty_image_is_migrated(self):
        '''
        This should not happened cause the image field is required,
        but this is a special case in AT's FileField.
        '''
        from Products.ATContentTypes.content.image import ATImage
        from plone.app.contenttypes.migration import ImageMigrator
        at_image = self.createATCTobject(ATImage, 'image')
        migrator = self.get_migrator(at_image, ImageMigrator)
        migrator.migrate()
        new_image = self.portal['image']
        self.assertEqual(new_image.image, None)

    def test_image_content_is_migrated(self):
        from plone.app.contenttypes.migration import ImageMigrator
        from plone.namedfile.interfaces import INamedImage
        from Products.ATContentTypes.content.image import ATImage

        # create the ATImage
        at_image = self.createATCTobject(ATImage, 'image')
        test_image_data = self.get_test_image_data()
        field = at_image.getField('image')
        field.set(at_image, test_image_data)
        field.setFilename(at_image, 'testimage.png')
        migrator = self.get_migrator(at_image, ImageMigrator)
        migrator.migrate()
        new_image = self.portal['image']
        self.assertTrue(INamedImage.providedBy(new_image.image))
        self.assertEqual(new_image.image.filename, 'testimage.png')
        self.assertEqual(new_image.image.contentType, 'image/png')
        self.assertEqual(new_image.image.data, test_image_data)

    def test_link_is_migrated(self):
        from Products.ATContentTypes.content.link import ATLink
        from plone.app.contenttypes.migration import LinkMigrator
        from plone.app.contenttypes.interfaces import ILink
        at_link = self.createATCTobject(ATLink, 'link')
        migrator = self.get_migrator(at_link, LinkMigrator)
        migrator.migrate()
        new_link = self.portal['link']
        self.assertTrue(ILink.providedBy(new_link))
        self.assertTrue(at_link is not new_link)

    def test_link_content_is_migrated(self):
        from plone.app.contenttypes.migration import LinkMigrator
        from plone.app.contenttypes.interfaces import ILink
        from Products.ATContentTypes.content.link import ATLink
        at_link = self.createATCTobject(ATLink, 'link')
        field = at_link.getField('remoteUrl')
        field.set(at_link, 'http://plone.org')
        migrator = self.get_migrator(at_link, LinkMigrator)
        migrator.migrate()
        new_link = self.portal['link']
        self.assertTrue(ILink.providedBy(new_link.link))
        self.assertEqual(new_link.link.remoteUrl, u'http://plone.org')

    def test_newsitem_is_migrated(self):
        from Products.ATContentTypes.content.newsitem import ATNewsItem
        from plone.app.contenttypes.migration import NewsItemMigrator
        from plone.app.contenttypes.interfaces import INewsItem
        at_newsitem = self.createATCTobject(ATNewsItem, 'newsitem')
        migrator = self.get_migrator(at_newsitem, NewsItemMigrator)
        migrator.migrate()
        new_newsitem = self.portal['newsitem']
        self.assertTrue(INewsItem.providedBy(new_newsitem))
        self.assertTrue(at_newsitem is not new_newsitem)

    def test_newsitem_content_is_migrated(self):
        from Products.ATContentTypes.content.newsitem import ATNewsItem
        from plone.app.contenttypes.migration import NewsItemMigrator
        from plone.namedfile.interfaces import INamedImage

        # create an ATNewsItem
        at_newsitem = self.createATCTobject(ATNewsItem, 'newsitem')
        at_newsitem.setText('Tütensuppe')
        at_newsitem.setImageCaption('Daniel Düsentrieb')
        test_image_data = self.get_test_image_data()
        image_field = at_newsitem.getField('image')
        image_field.set(at_newsitem, test_image_data)
        image_field.setFilename(at_newsitem, 'testimage.png')

        # migrate
        migrator = self.get_migrator(at_newsitem, NewsItemMigrator)
        migrator.migrate()

        # assertions
        new_newsitem = self.portal['newsitem']
        self.assertTrue(INamedImage.providedBy(new_newsitem.image))
        self.assertEqual(new_newsitem.image.filename, 'testimage.png')
        self.assertEqual(new_newsitem.image.contentType, 'image/png')
        self.assertEqual(new_newsitem.image.data, test_image_data)

        self.assertEqual(new_newsitem.text, u'Tütensuppe')
        self.assertEqual(new_newsitem.image_caption, u'Daniel Düsentrieb')
