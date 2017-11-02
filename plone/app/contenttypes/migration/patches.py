# -*- coding: utf-8 -*-
"""Patches used for migrations. These patches are applied before and removed
after running the migration.
"""
from plone.dexterity.content import DexterityContent
from plone.registry.interfaces import IRegistry
from Products.Archetypes.ExtensibleMetadata import ExtensibleMetadata
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFPlone.DublinCore import DefaultDublinCoreImpl
from Products.CMFPlone.interfaces import IEditingSchema
from Products.contentmigration.utils import patch
from Products.contentmigration.utils import undoPatch
from Products.PluginIndexes.common.UnIndex import _marker
from Products.PluginIndexes.UUIDIndex.UUIDIndex import UUIDIndex
from zope.component import getUtility
from zope.component import queryUtility

import os


def pass_fn(*args, **kwargs):
    """Empty function used for patching."""
    pass


def patched_index_object(*args, **kwargs):
    """Patched Products.ZCTextIndex.ZCTextIndex.ZCTextIndex.index_object"""
    return 0


# Prevent UUID Error-Messages when migrating folders.
# Products.PluginIndexes.UUIDIndex.UUIDIndex.UUIDIndex.insertForwardIndexEntry
def patched_insertForwardIndexEntry(self, entry, documentId):
    """Take the entry provided and put it in the correct place
    in the forward index.
    """
    if entry is None:
        return

    old_docid = self._index.get(entry, _marker)
    if old_docid is _marker:
        self._index[entry] = documentId
        self._length.change(1)


def patch_before_migration(patch_searchabletext=False):
    """Patch various things that make migration harder."""
    # Switch linkintegrity off
    ptool = queryUtility(IPropertiesTool)
    site_props = getattr(ptool, 'site_properties', None)
    if site_props and site_props.hasProperty(
            'enable_link_integrity_checks'):
        link_integrity = site_props.getProperty(
            'enable_link_integrity_checks', False)
        site_props.manage_changeProperties(
            enable_link_integrity_checks=False)
    else:
        # Plone 5
        registry = getUtility(IRegistry)
        editing_settings = registry.forInterface(
            IEditingSchema, prefix='plone')
        link_integrity = editing_settings.enable_link_integrity_checks
        editing_settings.enable_link_integrity_checks = False

    # Patch notifyModified to prevent setModificationDate() on changes
    # notifyModified lives in several places and is also used on folders
    # when their content changes.
    # So when we migrate Documents before Folders the folders
    # ModifiedDate gets changed
    PATCH_NOTIFY = [
        DexterityContent,
        DefaultDublinCoreImpl,
        ExtensibleMetadata
    ]
    for klass in PATCH_NOTIFY:
        patch(klass, 'notifyModified', pass_fn)

    # Disable queueing of indexing/reindexing/unindexing
    queue_indexing = os.environ.get('CATALOG_OPTIMIZATION_DISABLED', None)
    os.environ['CATALOG_OPTIMIZATION_DISABLED'] = '1'

    # Patch UUIDIndex
    patch(
        UUIDIndex,
        'insertForwardIndexEntry',
        patched_insertForwardIndexEntry)

    # Patch SearchableText index
    if patch_searchabletext:
        patch_indexing_at_blobs()
        patch_indexing_dx_blobs()

    return link_integrity, queue_indexing, patch_searchabletext


def undo_patch_after_migration(link_integrity=True,
                               queue_indexing=None,
                               patch_searchabletext=False,
                               ):
    """Revert to the original state."""

    # Switch linkintegrity back to what it was before migrating
    ptool = queryUtility(IPropertiesTool)
    site_props = getattr(ptool, 'site_properties', None)
    if site_props and site_props.hasProperty(
            'enable_link_integrity_checks'):
        site_props.manage_changeProperties(
            enable_link_integrity_checks=link_integrity
        )
    else:
        # Plone 5
        registry = getUtility(IRegistry)
        editing_settings = registry.forInterface(
            IEditingSchema, prefix='plone')
        editing_settings.enable_link_integrity_checks = link_integrity

    # Switch on setModificationDate on changes
    PATCH_NOTIFY = [
        DexterityContent,
        DefaultDublinCoreImpl,
        ExtensibleMetadata
    ]
    for klass in PATCH_NOTIFY:
        undoPatch(klass, 'notifyModified')

    # Reset queueing of indexing/reindexing/unindexing
    if queue_indexing is not None:
        os.environ['CATALOG_OPTIMIZATION_DISABLED'] = queue_indexing
    else:
        del os.environ['CATALOG_OPTIMIZATION_DISABLED']

    # Unpatch UUIDIndex
    undoPatch(UUIDIndex, 'insertForwardIndexEntry')

    # Unpatch SearchableText index
    if patch_searchabletext:
        unpatch_indexing_at_blobs()
        unpatch_indexing_dx_blobs()


def patch_indexing_at_blobs():
    from plone.app.blob.content import ATBlob
    patch(ATBlob, 'getIndexValue', pass_fn)


def unpatch_indexing_at_blobs():
    from plone.app.blob.content import ATBlob
    undoPatch(ATBlob, 'getIndexValue')


def patch_indexing_dx_blobs():
    from Products.ZCTextIndex.ZCTextIndex import ZCTextIndex
    patch(ZCTextIndex, 'index_object', patched_index_object)


def unpatch_indexing_dx_blobs():
    from Products.ZCTextIndex.ZCTextIndex import ZCTextIndex
    undoPatch(ZCTextIndex, 'index_object')
