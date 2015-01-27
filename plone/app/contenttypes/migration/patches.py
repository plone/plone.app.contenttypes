# -*- coding: utf-8 -*-
"""Patches used for migrations. These patches are applied before and removed
after running the migration.
"""
from Products.PluginIndexes.common.UnIndex import _marker


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
    # elif old_docid != documentId:
    #     logger.error("A different document with value '%s' already "
    #         "exists in the index.'" % entry)
