'''
Migrating ATContentTypes to plone.app.contenttypes objects.

This module imports from Product.contentmigration on which we depend
only in the setuptools extra_requiers [migrate_atct]. Importing this
will module will only work if P.contentmigration is installed so make sure
you catch ImportErrors
'''

from StringIO import StringIO

from Products.CMFPlone.utils import safe_unicode
from Products.contentmigration.basemigrator.migrator import CMFItemMigrator
from Products.contentmigration.basemigrator.walker import CatalogWalker

from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedFile, NamedImage


def migrate(portal, migrator):
    walker = CatalogWalker(portal, migrator)
    return walker.go()


class DocumentMigrator(CMFItemMigrator):

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


class FileMigrator(CMFItemMigrator):

    src_portal_type = 'File'
    src_meta_type = 'AT File'
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


class ImageMigrator(CMFItemMigrator):

    src_portal_type = 'Image'
    src_meta_type = 'AT Image'
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


class LinkMigrator(CMFItemMigrator):

    src_portal_type = 'Link'
    src_meta_type = 'AT Link'
    dst_portal_type = 'Link'
    dst_meta_type = None  # not used

    def migrate_schema_fields(self):
        remoteUrl = self.old.getField('remoteUrl').get(self.old)
        self.new.remoteUrl = remoteUrl


def migrate_links(portal):
    return migrate(portal, LinkMigrator)


class NewsItemMigrator(ImageMigrator, DocumentMigrator):

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
