# -*- coding: utf-8 -*-
'''
Migrating ATContentTypes to plone.app.contenttypes objects.

This module imports from Product.contentmigration on which we depend
only in the setuptools extra_requiers [migrate_atct]. Importing this
will module will only work if P.contentmigration is installed so make sure
you catch ImportErrors
'''

from Products.ATContentTypes.interfaces.interfaces import IATContentType
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.contentmigration.basemigrator.migrator import (CMFFolderMigrator,
                                                             CMFItemMigrator)
from Products.contentmigration.basemigrator.walker import CatalogWalker
from StringIO import StringIO
from persistent.list import PersistentList
from plone.app.textfield.value import RichTextValue
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.interfaces import IDexterityContent
from plone.namedfile.file import (NamedFile,
                                  NamedImage,
                                  NamedBlobFile,
                                  NamedBlobImage)
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


def migrate(portal, migrator):
    walker = CatalogWalker(portal, migrator)
    return walker.go()


def restoreReferences(portal):
    """ iterate over all Dexterity Objs and restore as Dexterity Reference. """
    out = ''
    catalog = getToolByName(portal, "portal_catalog")
    uid_catalog = getToolByName(portal, 'uid_catalog')
    # Seems that these newly created objs are not reindexed
    catalog.clearFindAndRebuild()
    intids = getUtility(IIntIds)
    results = catalog.searchResults(
        object_provides=IDexterityContent.__identifier__)
    for brain in results:
        obj = brain.getObject()

        # refs
        try:
            if not getattr(obj, 'relatedItems', None):
                obj.relatedItems = PersistentList()
            elif type(obj.relatedItems) != type(PersistentList()):
                obj.relatedItems = PersistentList(obj.relatedItems)
            for uuid in obj._relatedItems:
                to_obj = uuidToObject(uuid)
                to_id = intids.getId(to_obj)
                obj.relatedItems.append(RelationValue(to_id))
                out += str('Restore Relation from %s to %s \n' % (obj, to_obj))
            # keep the _relatedItems to restore the order
            # del obj._relatedItems
        except AttributeError:
            pass

        # backrefs
        try:
            backrefobjs = [uuidToObject(uuid) for uuid in obj._backrefs]
            for backrefobj in backrefobjs:
                # Dexterity and
                if IDexterityContent.providedBy(backrefobj):
                    relitems = getattr(backrefobj, 'relatedItems', None)
                    if not relitems:
                        backrefobj.relatedItems = PersistentList()
                    elif type(relitems) != type(PersistentList()):
                        backrefobj.relatedItems = PersistentList(
                            obj.relatedItems
                        )
                    to_id = intids.getId(obj)
                    backrefobj.relatedItems.append(RelationValue(to_id))

                # Archetypes
                elif IATContentType.providedBy(backrefobj):
                    # reindex UID so we are able to set the reference
                    path = '/'.join(obj.getPhysicalPath())
                    uid_catalog.catalog_object(obj, path)
                    backrefobj.setRelatedItems(obj)
                out += str(
                    'Restore BackRelation from %s to %s \n' % (
                        backrefobj,
                        obj
                    )
                )
            del obj._backrefs
        except AttributeError:
            pass
    return out


def restoreReferencesOrder(portal):
    """ In obj._relatedItems is the correct order of references. Let's
        replace the ATReference (UID) by the new Dexterity Refeŕence.
        Then we have a list with ordered Refs and can replace
        obj.relatedItems."""
    out = ''
    catalog = getToolByName(portal, "portal_catalog")
    results = catalog.searchResults(
        object_provides=IDexterityContent.__identifier__)
    # Iteration on all dexterity objects
    for brain in results:
        obj = brain.getObject()
        if not getattr(obj, '_relatedItems', None):
            continue
        # In obj._relatedItems we have the right order.
        atRelItems = obj._relatedItems
        # Replace the AT Ref by the Dex. Ref
        for i in atRelItems:
            for rel in obj.relatedItems:
                if rel.to_object.UID() == i:
                    atRelItems[atRelItems.index(i)] = rel
                    break
        obj.relatedItems = atRelItems
        del obj._relatedItems
        out += str('%s ordered.' % obj)
    return out


class ReferenceMigrator:

    def migrate_relatedItems(self):
        """ Store Archetype relations as target uids on the dexterity object
            for later restore. Backrelations are saved as well because all
            relation to deleted objects would be lost.
        """
        # Relations:
        relItems = self.old.getRelatedItems()
        relUids = [item.UID() for item in relItems]
        self.new._relatedItems = relUids

        # Backrefs:
        reference_catalog = getToolByName(self.old, REFERENCE_CATALOG)
        backrefs = [i.sourceUID for i in reference_catalog.getBackReferences(
            self.old, relationship="relatesTo")]
        self.new._backrefs = backrefs


class DocumentMigrator(CMFItemMigrator, ReferenceMigrator):

    src_portal_type = 'Document'
    src_meta_type = 'ATDocument'
    dst_portal_type = 'Document'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
        field = self.old.getField('text')
        mime_type = field.getContentType(self.old)
        raw_text = safe_unicode(field.getRaw(self.old))
        if raw_text.strip() == '':
            return
        richtext = RichTextValue(raw=raw_text, mimeType=mime_type,
                                 outputMimeType='text/x-html-safe')
        self.new.text = richtext


def migrate_documents(portal):
    return migrate(portal, DocumentMigrator)


class FileMigrator(CMFItemMigrator, ReferenceMigrator):

    src_portal_type = 'File'
    src_meta_type = 'ATFile'
    dst_portal_type = 'File'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
        old_file = self.old.getField('file').get(self.old)
        filename = safe_unicode(old_file.filename)
        namedfile = NamedFile(contentType=old_file.content_type,
                              data=StringIO(old_file.data),
                              filename=filename)
        self.new.file = namedfile


def migrate_files(portal):
    return migrate(portal, FileMigrator)


class BlobFileMigrator(CMFItemMigrator, ReferenceMigrator):

    src_portal_type = 'File'
    src_meta_type = 'ATBlob'
    dst_portal_type = 'File'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
        old_file = self.old.getField('file').get(self.old)
        filename = safe_unicode(old_file.filename)
        namedblobfile = NamedBlobFile(contentType=old_file.content_type,
                                      data=old_file.data,
                                      filename=filename)
        self.new.file = namedblobfile


def migrate_blobfiles(portal):
    return migrate(portal, BlobFileMigrator)


class ImageMigrator(CMFItemMigrator, ReferenceMigrator):

    src_portal_type = 'Image'
    src_meta_type = 'ATImage'
    dst_portal_type = 'Image'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
        old_image = self.old.getField('image').get(self.old)
        if old_image == '':
            return
        filename = safe_unicode(old_image.filename)
        namedimage = NamedImage(data=StringIO(old_image.data),
                                filename=filename)
        self.new.image = namedimage


def migrate_images(portal):
    return migrate(portal, ImageMigrator)


class BlobImageMigrator(CMFItemMigrator, ReferenceMigrator):

    src_portal_type = 'Image'
    src_meta_type = 'ATBlob'
    dst_portal_type = 'Image'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):

        old_image = self.old.getField('image').get(self.old)
        if old_image == '':
            return
        filename = safe_unicode(old_image.filename)
        namedblobimage = NamedBlobImage(data=old_image.data,
                                        filename=filename)
        self.new.image = namedblobimage


def migrate_blobimages(portal):
    return migrate(portal, BlobImageMigrator)


class LinkMigrator(CMFItemMigrator, ReferenceMigrator):

    src_portal_type = 'Link'
    src_meta_type = 'ATLink'
    dst_portal_type = 'Link'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
        remoteUrl = self.old.getField('remoteUrl').get(self.old)
        self.new.remoteUrl = remoteUrl


def migrate_links(portal):
    return migrate(portal, LinkMigrator)


class NewsItemMigrator(ImageMigrator, DocumentMigrator, ReferenceMigrator):

    src_portal_type = 'News Item'
    src_meta_type = 'ATNewsItem'
    dst_portal_type = 'News Item'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
        # migrate the image and text
        ImageMigrator.migrate_schema_fields(self)
        DocumentMigrator.migrate_schema_fields(self)

        # migrate the rest of the Schema
        self.new.image_caption = safe_unicode(
            self.old.getField('imageCaption').get(self.old))


def migrate_newsitems(portal):
    return migrate(portal, NewsItemMigrator)


class FolderMigrator(CMFFolderMigrator, ReferenceMigrator):

    src_portal_type = 'Folder'
    src_meta_type = 'ATFolder'
    dst_portal_type = 'Folder'
    dst_meta_type = None  # not used


def migrate_folders(portal):
    return migrate(portal, FolderMigrator)
