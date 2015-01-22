# -*- coding: utf-8 -*-
from Products.ATContentTypes.interfaces.document import IATDocument
from Products.ATContentTypes.interfaces.event import IATEvent
from Products.ATContentTypes.interfaces.file import IATFile
from Products.ATContentTypes.interfaces.folder import IATFolder
from Products.ATContentTypes.interfaces.image import IATImage
from Products.ATContentTypes.interfaces.link import IATLink
from Products.ATContentTypes.interfaces.news import IATNewsItem
from Products.ATContentTypes.interfaces.topic import IATTopic
from Products.CMFCore.utils import getToolByName
from plone.app.blob.interfaces import IATBlobFile
from plone.app.blob.interfaces import IATBlobImage
from plone.app.contenttypes import _
from plone.app.contenttypes.migration import migration
from plone.app.contenttypes.migration.utils import isSchemaExtended
from plone.app.contenttypes.migration.topics import migrate_topics
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

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
        'type_name': 'Folder',
        'old_meta_type': 'ATFolder',
    },
    "Document": {
        'iface': IATDocument,
        'migrator': migration.migrate_documents,
        'extended_fields': [],
        'type_name': 'Document',
        'old_meta_type': 'ATDocument',
    },
    # File without blobs
    "File": {
        'iface': IATFile,
        'migrator': migration.migrate_files,
        'extended_fields': [],
        'type_name': 'File',
        'old_meta_type': 'ATFile',
    },
    # Image without blobs
    "Image": {
        'iface': IATImage,
        'migrator': migration.migrate_images,
        'extended_fields': [],
        'type_name': 'Image',
        'old_meta_type': 'ATImage',
    },
    "News Item": {
        'iface': IATNewsItem,
        'migrator': migration.migrate_newsitems,
        'extended_fields': [],
        'type_name': 'News Item',
        'old_meta_type': 'ATNewsItem',
    },
    "Link": {
        'iface': IATLink,
        'migrator': migration.migrate_links,
        'extended_fields': [],
        'type_name': 'Link',
        'old_meta_type': 'ATLink',
    },
    "Event": {
        'iface': IATEvent,
        'migrator': migration.migrate_events,
        'extended_fields': [],
        'type_name': 'Event',
        'old_meta_type': 'ATEvent',
    },
    "BlobImage": {
        'iface': IATBlobImage,
        'migrator': migration.migrate_blobimages,
        'extended_fields': ['image'],
        'type_name': 'Image',
        'old_meta_type': 'ATBlob',
    },
    "BlobFile": {
        'iface': IATBlobFile,
        'migrator': migration.migrate_blobfiles,
        'extended_fields': ['file'],
        'type_name': 'File',
        'old_meta_type': 'ATBlob',
    },
    "Topic": {
        'iface': IATTopic,
        'migrator': migrate_topics,
        'extended_fields': [],
        'type_name': 'Collection',
        'old_meta_type': 'ATTopic',
    },
}

if HAS_APP_COLLECTION:
    ATCT_LIST["Collection"] = {
        'iface': ICollection,
        'migrator': migration.migrate_collections,
        'extended_fields': [],
        'type_name': 'Collection',
        'old_meta_type': 'Collection',
    }


def get_terms(context, counter, ext_dict, show_extended):
    """Takes dicts of types and their numbers and their extended fields
    Returns a list of SimpleVocabularyTerms:
    value = meta_type,
    token = meta_type,
    title = translated_meta_type (number_of_instances) - extended fields: list
    """
    results = []
    for k, v in counter.iteritems():
        if not show_extended:
            if k not in ext_dict:
                display = u"{0} ({1})".format(context.translate(_(k)), v)
                term = SimpleVocabulary.createTerm(k, k, display)
                results.append(term)
        else:
            if k in ext_dict:
                ext = str(ext_dict[k]['fields']).\
                    replace("[", "").replace("]", "")
                display = u"{0} ({1}) - extended fields: {2}".\
                    format(context.translate(_(k)), v, ext)
                term = SimpleVocabulary.createTerm(k, k, display)
                results.append(term)
    results.sort(key=lambda x: x.title)
    return results


def count(brains):
    """Turns a list of brains into a dict {<meta_type>:<number_of_instances>,}
    Since Image and File both have the meta_type 'ATBlob' they are handled
    differently.
    """
    counter = {}
    for brain in brains:
        pt = brain.portal_type
        if "Blob" in brain.meta_type:
            if pt == "File":
                pt = "BlobFile"
            else:
                pt = "BlobImage"
        if not counter.get(pt):
            counter[pt] = 0
        if not brain.meta_type or 'dexterity' in brain.meta_type.lower():
            # There might be DX types with same iface and meta_type than AT
            continue
        counter[pt] += 1
    return counter


def results(context, show_extended=False):
    """Helper method to create the vocabularies used below.
    Searches the catalog for AT-meta_types to get all Archetypes content.
    If show_extended is true the returned SimpleVocabulary will include
    types that are extended beyond what is expected.
    """
    ext_dict = {}
    meta_types = []
    for k, v in ATCT_LIST.items():
        extendend_fields = isSchemaExtended(v['iface'])
        expected = v['extended_fields']
        is_extended = len(extendend_fields) > len(expected)
        if is_extended and show_extended:
            meta_types.append(v['old_meta_type'])
            ext_dict[k] = {}
            if expected:
                extendend_fields.remove(expected[0])
            ext_dict[k]['fields'] = extendend_fields

        elif not show_extended and not is_extended:
            meta_types.append(v['old_meta_type'])
    catalog = getToolByName(context, "portal_catalog")
    brains = catalog.search({'meta_type': meta_types})
    counter = count(brains)

    return SimpleVocabulary(get_terms(context,
                                      counter,
                                      ext_dict,
                                      show_extended))


class ATCTypesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        """Return a vocabulary with standard content types
        and, for each one, the number of occurrences.
        """
        return results(context, show_extended=False)


class ExtendedTypesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        """Return a vocabulary with all extended types
        and for each the number of occurences and a list of the
        extended fields.
        """
        return results(context, show_extended=True)


class ChangedBaseClasses(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        """Return a vocabulary with all changed base classes."""
        from plone.app.contenttypes.migration.dxmigration import \
            list_of_changed_base_class_names
        list_of_class_names = list_of_changed_base_class_names(context) or {}
        return SimpleVocabulary(
            [SimpleVocabulary.createTerm(
                class_name, class_name,
                '{0} ({1})'.format(
                    class_name, list_of_class_names[class_name]))
             for class_name in list_of_class_names.keys()]
        )
