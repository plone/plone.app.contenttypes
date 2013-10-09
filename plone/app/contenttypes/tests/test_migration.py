# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from five.intid.intid import IntIds
from five.intid.site import addUtility
from plone.app.contenttypes.migration.migration import restoreReferences
from plone.app.contenttypes.testing import \
    PLONE_APP_CONTENTTYPES_MIGRATION_TESTING
from plone.event.interfaces import IEventAccessor
from plone.app.testing import login
from plone.app.testing import applyProfile
from zope.component import getSiteManager
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.schema.interfaces import IVocabularyFactory

import os.path
import transaction
import unittest2 as unittest


class MigrateToATContentTypesTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_MIGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        self.request['URL'] = self.portal.absolute_url()
        self.catalog = getToolByName(self.portal, "portal_catalog")
        self.portal.acl_users.userFolderAddUser('admin',
                                                'secret',
                                                ['Manager'],
                                                [])
        login(self.portal, 'admin')
        self.portal.portal_workflow.setDefaultChain(
            "simple_publication_workflow")
        transaction.commit()

    def tearDownPloneSite(self, portal):
        try:
            applyProfile(self.portal, 'plone.app.contenttypes:uninstall')
        except KeyError:
            pass

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

    def createATCTobject(self, klass, id, parent=None):
        '''Borrowed from ATCTFieldTestCase'''
        import transaction
        parent = parent if parent else self.portal
        obj = klass(oid=id)
        parent[id] = obj
        transaction.savepoint()
        # need to aq wrap after the savepoint. wrapped content can't be pickled
        obj = obj.__of__(parent)
        obj.initializeArchetype()
        return obj

    def test_assert_at_contenttypes(self):
        from plone.app.contenttypes.interfaces import IDocument
        self.portal.invokeFactory('Document', 'document')
        at_document = self.portal['document']
        self.assertEqual('ATDocument', at_document.meta_type)
        self.assertFalse(IDocument.providedBy(at_document))

    def test_dx_content_is_indexed(self):
        from plone.app.contenttypes.migration.migration import DocumentMigrator
        from plone.app.contenttypes.interfaces import IDocument
        self.portal.invokeFactory('Document', 'document')
        at_document = self.portal['document']
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_document, DocumentMigrator)
        migrator.migrate()
        brains = self.catalog(object_provides=IDocument.__identifier__)
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getObject(), self.portal["document"])

    def test_old_content_is_removed(self):
        from plone.app.contenttypes.migration.migration import DocumentMigrator
        self.portal.invokeFactory('Document', 'document')
        at_document = self.portal['document']
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_document, DocumentMigrator)
        migrator.migrate()
        brains = self.catalog(portal_type='Document')
        self.assertEqual(len(brains), 1)

    def test_old_content_is_unindexed(self):
        from Products.ATContentTypes.interfaces import IATDocument
        from plone.app.contenttypes.migration.migration import DocumentMigrator
        self.portal.invokeFactory('Document', 'document')
        at_document = self.portal['document']
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_document, DocumentMigrator)
        brains = self.catalog(object_provides=IATDocument.__identifier__)
        self.assertEqual(len(brains), 1)
        migrator.migrate()
        brains = self.catalog(object_provides=IATDocument.__identifier__)
        self.assertEqual(len(brains), 0)

    def test_document_is_migrated(self):
        from plone.app.contenttypes.migration.migration import DocumentMigrator
        from plone.app.contenttypes.interfaces import IDocument
        self.portal.invokeFactory('Document', 'document')
        at_document = self.portal['document']
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_document, DocumentMigrator)
        migrator.migrate()
        dx_document = self.portal['document']
        self.assertTrue(IDocument.providedBy(dx_document))
        self.assertTrue(at_document is not dx_document)

    def test_collection_is_migrated(self):
        from plone.app.contenttypes.migration.migration import\
            CollectionMigrator
        from plone.app.contenttypes.interfaces import ICollection
        if 'Collection' in self.portal.portal_types.keys():
            self.portal.invokeFactory('Collection', 'collection')
            at_collection = self.portal['collection']
            applyProfile(self.portal, 'plone.app.contenttypes:default')
            migrator = self.get_migrator(at_collection, CollectionMigrator)
            migrator.migrate()
            dx_collection = self.portal['collection']
            self.assertTrue(ICollection.providedBy(dx_collection))
            self.assertTrue(at_collection is not dx_collection)

    def test_document_content_is_migrated(self):
        from plone.app.contenttypes.migration.migration import DocumentMigrator
        from plone.app.textfield.interfaces import IRichTextValue

        # create an ATDocument
        self.portal.invokeFactory('Document', 'document')
        at_document = self.portal['document']
        at_document.setText('Tütensuppe')
        at_document.setContentType('chemical/x-gaussian-checkpoint')

        # migrate
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_document, DocumentMigrator)
        migrator.migrate()

        # assertions
        dx_document = self.portal['document']
        self.assertTrue(IRichTextValue(dx_document.text))
        self.assertEqual(dx_document.text.raw, u'Tütensuppe')
        self.assertEqual(dx_document.text.mimeType,
                         'chemical/x-gaussian-checkpoint')
        self.assertEqual(dx_document.text.outputMimeType, 'text/x-html-safe')

    def test_document_excludefromnav_is_migrated(self):
        from plone.app.contenttypes.migration.migration import DocumentMigrator

        # create an ATDocument
        self.portal.invokeFactory('Document', 'document')
        at_document = self.portal['document']
        at_document.setExcludeFromNav(True)

        # migrate
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_document, DocumentMigrator)
        migrator.migrate()

        # assertions
        dx_document = self.portal['document']
        self.assertTrue(dx_document.exclude_from_nav)

    def test_file_is_migrated(self):
        from Products.ATContentTypes.content.file import ATFile
        from plone.app.contenttypes.migration.migration import FileMigrator
        from plone.app.contenttypes.interfaces import IFile
        at_file = self.createATCTobject(ATFile, 'file')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_file, FileMigrator)
        migrator.migrate()
        dx_file = self.portal['file']
        self.assertTrue(IFile.providedBy(dx_file))
        self.assertTrue(at_file is not dx_file)

    def test_file_content_is_migrated(self):
        from plone.app.contenttypes.migration.migration import FileMigrator
        from plone.namedfile.interfaces import INamedBlobFile
        from Products.ATContentTypes.content.file import ATFile
        at_file = self.createATCTobject(ATFile, 'file')
        field = at_file.getField('file')
        field.set(at_file, 'dummydata')
        field.setFilename(at_file, 'dummyfile.txt')
        field.setContentType(at_file, 'text/dummy')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_file, FileMigrator)
        migrator.migrate()
        dx_file = self.portal['file']
        self.assertTrue(INamedBlobFile.providedBy(dx_file.file))
        self.assertEqual(dx_file.file.filename, 'dummyfile.txt')
        self.assertEqual(dx_file.file.contentType, 'text/dummy')
        self.assertEqual(dx_file.file.data, 'dummydata')

    def test_image_is_migrated(self):
        from Products.ATContentTypes.content.image import ATImage
        from plone.app.contenttypes.migration.migration import ImageMigrator
        from plone.app.contenttypes.interfaces import IImage
        at_image = self.createATCTobject(ATImage, 'image')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_image, ImageMigrator)
        migrator.migrate()
        dx_image = self.portal['image']
        self.assertTrue(IImage.providedBy(dx_image))
        self.assertTrue(at_image is not dx_image)

    def test_empty_image_is_migrated(self):
        """
        This should not happened cause the image field is required,
        but this is a special case in AT's FileField.
        """
        from Products.ATContentTypes.content.image import ATImage
        from plone.app.contenttypes.migration.migration import ImageMigrator
        at_image = self.createATCTobject(ATImage, 'image')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_image, ImageMigrator)
        migrator.migrate()
        dx_image = self.portal['image']
        self.assertEqual(dx_image.image, None)

    def test_image_content_is_migrated(self):
        from plone.app.contenttypes.migration.migration import ImageMigrator
        from plone.namedfile.interfaces import INamedBlobImage
        from Products.ATContentTypes.content.image import ATImage

        # create the ATImage
        at_image = self.createATCTobject(ATImage, 'image')
        test_image_data = self.get_test_image_data()
        field = at_image.getField('image')
        field.set(at_image, test_image_data)
        field.setFilename(at_image, 'testimage.png')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_image, ImageMigrator)
        migrator.migrate()
        dx_image = self.portal['image']
        self.assertTrue(INamedBlobImage.providedBy(dx_image.image))
        self.assertEqual(dx_image.image.filename, 'testimage.png')
        self.assertEqual(dx_image.image.contentType, 'image/png')
        self.assertEqual(dx_image.image.data, test_image_data)

    def test_blob_file_is_migrated(self):
        from plone.app.contenttypes.migration.migration import BlobFileMigrator
        from plone.app.contenttypes.interfaces import IFile
        self.portal.invokeFactory('File', 'file')
        at_file = self.portal['file']
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_file, BlobFileMigrator)
        migrator.migrate()
        dx_file = self.portal['file']
        self.assertTrue(IFile.providedBy(dx_file))
        self.assertTrue(at_file is not dx_file)

    def test_blob_file_content_is_migrated(self):
        from plone.app.contenttypes.migration.migration import BlobFileMigrator
        from plone.namedfile.interfaces import INamedBlobFile
        self.portal.invokeFactory('File', 'file')
        at_file = self.portal['file']
        at_file.setFile('dummydata',
                        mimetype="text/dummy",
                        filename='dummyfile.txt')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_file, BlobFileMigrator)
        migrator.migrate()
        dx_file = self.portal['file']
        self.assertTrue(INamedBlobFile.providedBy(dx_file.file))
        self.assertEqual(dx_file.file.filename, 'dummyfile.txt')
        self.assertEqual(dx_file.file.contentType, 'text/dummy')
        self.assertEqual(dx_file.file.data, 'dummydata')

    def test_blob_image_is_migrated(self):
        from plone.app.contenttypes.migration.migration import\
            BlobImageMigrator
        from plone.app.contenttypes.interfaces import IImage
        self.portal.invokeFactory('Image', 'image')
        at_image = self.portal['image']
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_image, BlobImageMigrator)
        migrator.migrate()
        dx_image = self.portal['image']
        self.assertTrue(IImage.providedBy(dx_image))
        self.assertTrue(at_image is not dx_image)

    def test_empty_blob_image_is_migrated(self):
        """
        This should not happened cause the image field is required,
        but this is a special case in AT's FileField.
        """
        from plone.app.contenttypes.migration.migration import\
            BlobImageMigrator
        self.portal.invokeFactory('Image', 'image')
        at_image = self.portal['image']
        migrator = self.get_migrator(at_image, BlobImageMigrator)
        migrator.migrate()
        dx_image = self.portal['image']
        self.assertEqual(dx_image.image.data, '')

    def test_blob_image_content_is_migrated(self):
        from plone.app.contenttypes.migration.migration import\
            BlobImageMigrator
        from plone.namedfile.interfaces import INamedBlobImage
        self.portal.invokeFactory('Image', 'image')
        at_image = self.portal['image']
        test_image_data = self.get_test_image_data()
        at_image.setImage(test_image_data, filename='testimage.png')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_image, BlobImageMigrator)
        migrator.migrate()
        dx_image = self.portal['image']
        self.assertTrue(INamedBlobImage.providedBy(dx_image.image))
        self.assertEqual(dx_image.image.filename, 'testimage.png')
        self.assertEqual(dx_image.image.contentType, 'image/png')
        self.assertEqual(dx_image.image.data, test_image_data)

    def test_link_is_migrated(self):
        from plone.app.contenttypes.migration.migration import LinkMigrator
        from plone.app.contenttypes.interfaces import ILink
        self.portal.invokeFactory('Link', 'link')
        at_link = self.portal['link']
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_link, LinkMigrator)
        migrator.migrate()
        dx_link = self.portal['link']
        self.assertTrue(ILink.providedBy(dx_link))
        self.assertTrue(dx_link is not at_link)

    def test_link_content_is_migrated(self):
        from plone.app.contenttypes.migration.migration import LinkMigrator
        from plone.app.contenttypes.interfaces import ILink
        self.portal.invokeFactory('Link', 'link')
        at_link = self.portal['link']
        field = at_link.getField('remoteUrl')
        field.set(at_link, 'http://plone.org')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_link, LinkMigrator)
        migrator.migrate()
        dx_link = self.portal['link']
        self.assertTrue(ILink.providedBy(dx_link.link))
        self.assertEqual(dx_link.link.remoteUrl, u'http://plone.org')

    def test_newsitem_is_migrated(self):
        from plone.app.contenttypes.migration.migration import NewsItemMigrator
        from plone.app.contenttypes.interfaces import INewsItem
        self.portal.invokeFactory('News Item', 'newsitem')
        at_newsitem = self.portal['newsitem']
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_newsitem, NewsItemMigrator)
        migrator.migrate()
        dx_newsitem = self.portal['newsitem']
        self.assertTrue(INewsItem.providedBy(dx_newsitem))
        self.assertTrue(at_newsitem is not dx_newsitem)

    def test_newsitem_content_is_migrated(self):
        from plone.app.contenttypes.migration.migration import NewsItemMigrator
        from plone.app.textfield.interfaces import IRichTextValue
        from plone.namedfile.interfaces import INamedBlobImage

        # create an ATNewsItem
        self.portal.invokeFactory('News Item', 'newsitem')
        at_newsitem = self.portal['newsitem']
        at_newsitem.setText('Tütensuppe')
        at_newsitem.setContentType('chemical/x-gaussian-checkpoint')
        at_newsitem.setImageCaption('Daniel Düsentrieb')
        test_image_data = self.get_test_image_data()
        image_field = at_newsitem.getField('image')
        image_field.set(at_newsitem, test_image_data)
        image_field.setFilename(at_newsitem, 'testimage.png')

        # migrate
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_newsitem, NewsItemMigrator)
        migrator.migrate()

        # assertions
        dx_newsitem = self.portal['newsitem']
        self.assertTrue(INamedBlobImage.providedBy(dx_newsitem.image))
        self.assertEqual(dx_newsitem.image.filename, 'testimage.png')
        self.assertEqual(dx_newsitem.image.contentType, 'image/png')
        self.assertEqual(dx_newsitem.image.data, test_image_data)

        self.assertEqual(dx_newsitem.image_caption, u'Daniel Düsentrieb')

        self.assertTrue(IRichTextValue(dx_newsitem.text))
        self.assertEqual(dx_newsitem.text.raw, u'Tütensuppe')
        self.assertEqual(dx_newsitem.text.mimeType,
                         'chemical/x-gaussian-checkpoint')
        self.assertEqual(dx_newsitem.text.outputMimeType, 'text/x-html-safe')

    def test_event_is_migrated(self):
        from DateTime import DateTime
        from plone.app.contenttypes.migration.migration import EventMigrator
        from plone.app.textfield.interfaces import IRichTextValue


        # create an ATEvent
        self.portal.invokeFactory('Event', 'event')
        at_event = self.portal['event']

        # Date
        start = DateTime('2013-01-01')
        end = DateTime('2013-02-01')
        at_event.getField('startDate').set(at_event, DateTime('2013-01-01'))
        at_event.getField('endDate').set(at_event, DateTime('2013-02-01'))

        # Contact
        at_event.getField('contactPhone').set(at_event, '123456789')
        at_event.getField('contactEmail').set(at_event, 'dummy@email.com')
        at_event.getField('contactName').set(at_event, 'Name')

        # URL
        at_event.getField('eventUrl').set(at_event, 'http://www.plone.org')

        # Attendees
        at_event.getField('attendees').set(at_event, ('You', 'Me'))

        # Text
        at_event.setText('Tütensuppe')
        at_event.setContentType('chemical/x-gaussian-checkpoint')

        # migrate
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_event, EventMigrator)
        migrator.migrate()

        # assertions
        dx_event = self.portal['event']

        dx_acc = IEventAccessor(dx_event)
        self.assertEqual('%s+00:00' % start.asdatetime().isoformat(),
                         dx_acc.start.isoformat())
        self.assertEqual('%s+00:00' % end.asdatetime().isoformat(),
                         dx_acc.end.isoformat())
        self.assertEqual('123456789', dx_acc.contact_phone)
        self.assertEqual('dummy@email.com', dx_acc.contact_email)
        self.assertEqual('Name', dx_acc.contact_name)
        self.assertEqual('http://www.plone.org', dx_acc.event_url)
        self.assertEqual(('You', 'Me'), dx_acc.attendees)

        self.assertTrue(IRichTextValue(dx_event.text))
        self.assertEqual(dx_event.text.raw, u'Tütensuppe')
        self.assertEqual(dx_event.text.mimeType,
                         'chemical/x-gaussian-checkpoint')
        self.assertEqual(dx_event.text.outputMimeType, 'text/x-html-safe')

        # self.assertEquals('Event', dx_event.__class__.__name__)

    def test_folder_is_migrated(self):
        from plone.app.contenttypes.migration.migration import FolderMigrator
        from plone.app.contenttypes.interfaces import IFolder
        self.portal.invokeFactory('Folder', 'folder')
        at_folder = self.portal['folder']
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_folder, FolderMigrator)
        migrator.migrate()
        dx_folder = self.portal['folder']
        self.assertTrue(IFolder.providedBy(dx_folder))
        self.assertTrue(at_folder is not dx_folder)

    def test_folder_children_are_migrated(self):
        from plone.app.contenttypes.migration.migration import FolderMigrator
        self.portal.invokeFactory('Folder', 'folder')
        at_folder = self.portal['folder']
        at_folder.invokeFactory('Document', 'document')
        at_child = at_folder['document']
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_folder, FolderMigrator)
        migrator.migrate()
        dx_folder = self.portal['folder']
        self.assertTrue(at_child in dx_folder.contentValues())

    def test_relations_are_migrated(self):
        from plone.app.contenttypes.migration.migration import DocumentMigrator

        # IIntIds is not registered in the test env. So register it here
        sm = getSiteManager(self.portal)
        addUtility(sm, IIntIds, IntIds, ofs_name='intids', findroot=False)

        # create three ATDocument
        self.portal.invokeFactory('Document', 'doc1')
        at_doc1 = self.portal['doc1']
        self.portal.invokeFactory('Document', 'doc2')
        at_doc2 = self.portal['doc2']
        self.portal.invokeFactory('Document', 'doc3')
        at_doc3 = self.portal['doc3']

        # relate them
        at_doc1.setRelatedItems([at_doc2.UID(), ])
        at_doc2.setRelatedItems([at_doc1, at_doc3])
        at_doc3.setRelatedItems(at_doc1)

        # migrate
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrator = self.get_migrator(at_doc1, DocumentMigrator)
        migrator.migrate()
        migrator = self.get_migrator(at_doc2, DocumentMigrator)
        migrator.migrate()
        migrator = self.get_migrator(at_doc3, DocumentMigrator)
        migrator.migrate()
        restoreReferences(self.portal)

        # assertions
        dx_doc1 = self.portal['doc1']
        dx_doc2 = self.portal['doc2']
        dx_doc3 = self.portal['doc3']

        self.assertEqual(len(dx_doc1.relatedItems), 1)
        rel1 = dx_doc1.relatedItems[0]
        self.assertEqual(rel1.to_object, dx_doc2)
        self.assertEqual(len(dx_doc2.relatedItems), 2)
        rel1 = dx_doc2.relatedItems[0]
        rel2 = dx_doc2.relatedItems[1]
        self.assertEqual(
            set([rel1.to_object, rel2.to_object]), set([dx_doc1, dx_doc3]))
        self.assertEqual(len(dx_doc3.relatedItems), 1)
        rel1 = dx_doc3.relatedItems[0]
        self.assertEqual(rel1.to_object, dx_doc1)

    def test_stats(self):
        from plone.app.contenttypes.migration.migration import DocumentMigrator
        from plone.app.contenttypes.migration.browser import \
            MigrateFromATContentTypes as MigrationView

        self.portal.invokeFactory('Document', 'doc1')
        at_doc1 = self.portal['doc1']
        self.portal.invokeFactory('Document', 'doc2')
        at_doc2 = self.portal['doc2']
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        migrationview = MigrationView(self.portal, None)
        stats = migrationview.stats()
        self.assertEqual(str(stats), "[('ATDocument', 2)]")
        migrator = self.get_migrator(at_doc1, DocumentMigrator)
        migrator.migrate()
        stats = migrationview.stats()
        self.assertEqual(str(stats), "[('ATDocument', 1), ('Document', 1)]")
        migrator = self.get_migrator(at_doc2, DocumentMigrator)
        migrator.migrate()
        stats = migrationview.stats()
        self.assertEqual(str(stats), "[('Document', 2)]")

    def test_migration_atctypes_vocabulary_registered(self):
        name = 'plone.app.contenttypes.migration.atctypes'
        factory = getUtility(IVocabularyFactory, name)
        self.assertIsNotNone(factory,
                             'Vocabulary %s does not exist' % name)

        vocabulary = factory(self.portal)
        self.assertEqual((), tuple(vocabulary))

    def test_migration_atctypes_vocabulary_result(self):
        from Products.ATContentTypes.content.document import ATDocument
        from Products.ATContentTypes.content.file import ATFile
        from Products.ATContentTypes.content.image import ATImage
        from Products.ATContentTypes.content.folder import ATFolder
        from Products.ATContentTypes.content.link import ATLink

        name = 'plone.app.contenttypes.migration.atctypes'
        factory = getUtility(IVocabularyFactory, name)

        self.createATCTobject(ATDocument, 'doc1')
        self.createATCTobject(ATDocument, 'doc2')
        self.createATCTobject(ATFile, 'file')
        self.createATCTobject(ATImage, 'image')
        self.createATCTobject(ATFolder, 'folder')
        self.createATCTobject(ATLink, 'link')

        vocabulary = factory(self.portal)

        self.assertEqual(
            5,
            len(vocabulary),
            'Expect 5 entries in vocab because there are 5 diffrent types')

        # Result format
        docs = [term for term in vocabulary if term.token == 'Document'][0]
        self.assertEqual('Document', docs.value)
        self.assertEqual('Document (2)', docs.title)

    def test_migration_extendedtypes_vocabulary_registered(self):
        name = 'plone.app.contenttypes.migration.extendedtypes'
        factory = getUtility(IVocabularyFactory, name)
        self.assertIsNotNone(factory,
                             'Vocabulary %s does not exist' % name)

        vocabulary = factory(self.portal)
        self.assertEqual((), tuple(vocabulary))

    def test_migration_extendedtypes_vocabulary_result(self):
        from archetypes.schemaextender.field import ExtensionField
        from archetypes.schemaextender.interfaces import ISchemaExtender
        from Products.Archetypes import atapi
        from Products.ATContentTypes.content.document import ATDocument
        from zope.component import adapts
        from zope.component import provideAdapter
        from zope.interface import classImplements
        from zope.interface import implements
        from zope.interface import Interface

        SCHEMA_EXTENDER_CACHE_KEY = '__archetypes_schemaextender_cache'

        name = 'plone.app.contenttypes.migration.extendedtypes'
        factory = getUtility(IVocabularyFactory, name)

        class IDummy(Interface):
            """Taggable content
            """

        classImplements(ATDocument, IDummy)
        doc = self.createATCTobject(ATDocument, 'doc')

        class DummyField(ExtensionField, atapi.StringField):
            """Dummy Field"""

        class DummySchemaExtender(object):
            implements(ISchemaExtender)
            adapts(IDummy)

            _fields = [DummyField('dummy')]

            def __init__(self, context):
                self.context = context

            def getFields(self):
                return self._fields

        provideAdapter(DummySchemaExtender, name=u"dummy.extender")

        # Clear cache
        delattr(self.request, SCHEMA_EXTENDER_CACHE_KEY)
        self.assertIn('dummy', doc.Schema()._names)

        vocabulary = factory(self.portal)

        self.assertEqual(1, len(vocabulary), 'Expect one entry')

        self.assertEqual("Document (1) - extended fields: 'dummy'",
                          tuple(vocabulary)[0].title)
