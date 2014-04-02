# -*- coding: utf-8 -*-
from Products.ATContentTypes.interfaces.document import IATDocument
from Products.ATContentTypes.interfaces.event import IATEvent
from Products.ATContentTypes.interfaces.file import IATFile
from Products.ATContentTypes.interfaces.folder import IATFolder
from Products.ATContentTypes.interfaces.image import IATImage
from Products.ATContentTypes.interfaces.link import IATLink
from Products.ATContentTypes.interfaces.news import IATNewsItem
from Products.CMFCore.utils import getToolByName
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from plone.app.blob.interfaces import IATBlobFile
from plone.app.blob.interfaces import IATBlobImage
from plone.app.contenttypes.migration import migration
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import getGlobalSiteManager
from zope.component.hooks import getSite

import pkg_resources

try:
    pkg_resources.get_distribution('plone.app.collection')
except pkg_resources.DistributionNotFound:
    ICollection = None
    HAS_APP_COLLECTION = False
else:
    HAS_APP_COLLECTION = True
    from plone.app.collection.interfaces import ICollection

ATCT_LIST = {
    "Folder": {
        'iface': IATFolder,
        'migrator': migration.migrate_folders,
        'extended_fields': [],
        'new_type_name': 'Folder',
        'old_meta_type': 'ATFolder',
    },
    "Document": {
        'iface': IATDocument,
        'migrator': migration.migrate_documents,
        'extended_fields': [],
        'new_type_name': 'Document',
        'old_meta_type': 'ATDocument',
    },
    "File": {
        'iface': IATFile,
        'migrator': migration.migrate_files,
        'extended_fields': ['file'],
        'new_type_name': 'File',
        'old_meta_type': 'ATFile',
    },
    "Image": {
        'iface': IATImage,
        'migrator': migration.migrate_images,
        'extended_fields': ['image'],
        'new_type_name': 'Image',
        'old_meta_type': 'ATImage',
    },
    "News Item": {
        'iface': IATNewsItem,
        'migrator': migration.migrate_newsitems,
        'extended_fields': [],
        'new_type_name': 'News Item',
        'old_meta_type': 'ATNewsItem',
    },
    "Link": {
        'iface': IATLink,
        'migrator': migration.migrate_links,
        'extended_fields': [],
        'new_type_name': 'Link',
        'old_meta_type': 'ATLink',
    },
    "Event": {
        'iface': IATEvent,
        'migrator': migration.migrate_events,
        'extended_fields': [],
        'new_type_name': 'Event',
        'old_meta_type': 'ATEvent',
    },
    "BlobImage": {
        'iface': IATBlobImage,
        'migrator': migration.migrate_blobimages,
        'extended_fields': ['image'],
        'new_type_name': 'Image',
        'old_meta_type': 'ATBlobImage',
    },
    "BlobFile": {
        'iface': IATBlobFile,
        'migrator': migration.migrate_blobfiles,
        'extended_fields': ['file'],
        'new_type_name': 'File',
        'old_meta_type': 'ATBlobFile',
    },
}

if HAS_APP_COLLECTION:
    ATCT_LIST["Collection"] = {
        'iface': ICollection,
        'migrator': migration.migrate_collections,
        'extended_fields': [],
        'new_type_name': 'Collection',
        'old_meta_type': 'Collection',
    }


def isSchemaExtended(iface):
    """Return a list of fields added by archetypes.schemaextender
    """
    fields = _compareSchemata(iface)
    fields2 = _checkForExtenderInterfaces(iface)
    fields.extend(fields2)
    return [i for i in set(fields)]


def _compareSchemata(interface):
    """Return a list of extended fields by archetypes.schemaextender
    by comparing the real and the default schemata.
    """
    portal = getSite()
    pc = portal.portal_catalog
    brains = pc(object_provides=interface.__identifier__)
    for brain in brains:
        if not brain.meta_type or 'dexterity' in brain.meta_type.lower():
            # There might be DX types with same iface and meta_type than AT
            continue
        obj = brain.getObject()
        real_fields = set(obj.Schema()._names)
        orig_fields = set(obj.schema._names)
        diff = [i for i in real_fields.difference(orig_fields)]
        return diff
    return []


def _checkForExtenderInterfaces(interface):
    """Return whether a specific content type interface
    is extended by archetypes.schemaextender or not.
    """
    sm = getGlobalSiteManager()
    extender_interfaces = [
        ISchemaExtender,
        ISchemaModifier,
        IBrowserLayerAwareExtender,
        IOrderableSchemaExtender,
    ]
    # We have a few possible interfaces to test
    # here, so get all the interfaces that
    # are for the given content type first
    registrations = \
        [a for a in sm.registeredAdapters() if interface in a.required]
    for adapter in registrations:
        if adapter.provided in extender_interfaces:
            fields = getattr(adapter.factory(None), 'fields', [])
            return [field.getName() for field in fields]
    return []


def installTypeIfNeeded(type_name):
    """Make sure the dexterity-fti is already installed.
    If not we run a step that only installs the types fti.
    """
    portal = getSite()
    tt = getToolByName(portal, 'portal_types')
    fti = tt.getTypeInfo(type_name)
    if IDexterityFTI.providedBy(fti):
        return
    ps = getToolByName(portal, 'portal_setup')
    profile_name = type_name.lower().replace('_', '')
    ps.runAllImportStepsFromProfile(
        'profile-plone.app.contenttypes:%s' % profile_name
    )
