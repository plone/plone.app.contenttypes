'''
Migrating ATContentTypes to plone.app.contenttypes objects.

This module imports from Product.contentmigration on which we depend
only in the setuptools extra_requiers [migrate_atct]. Importing this
will module will only work if P.contentmigration is installed so make sure
you catch ImportErrors
'''

from Products.contentmigration.basemigrator.migrator import CMFItemMigrator
from Products.contentmigration.basemigrator.walker import CatalogWalker


def migrate(portal, migrator):
    walker = CatalogWalker(portal, migrator)
    return walker.go()


class DocumentMigrator(CMFItemMigrator):

    src_portal_type = 'Document'
    src_meta_type = 'ATDocument'
    dst_portal_type = 'Document'
    dst_meta_type = None  # not used


def migrate_documents(portal):
    return migrate(portal, DocumentMigrator)
