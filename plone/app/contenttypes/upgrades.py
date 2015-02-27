# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.app.contenttypes.utils import DEFAULT_TYPES
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import queryUtility
import logging
logger = logging.getLogger(name="plone.app.contenttypes upgrade")


def update_fti(context):
    """ Schema-files moved into their own folder after 1.0b1
    """
    # Document
    fti = queryUtility(
        IDexterityFTI,
        name='Document'
    )
    fti.model_file = "plone.app.contenttypes.schema:document.xml"
    # File
    fti = queryUtility(
        IDexterityFTI,
        name='File'
    )
    fti.model_file = "plone.app.contenttypes.schema:file.xml"
    # Folder
    fti = queryUtility(
        IDexterityFTI,
        name='Folder'
    )
    fti.model_file = "plone.app.contenttypes.schema:folder.xml"
    # Image
    fti = queryUtility(
        IDexterityFTI,
        name='Image'
    )
    fti.model_file = "plone.app.contenttypes.schema:image.xml"
    # Link
    fti = queryUtility(
        IDexterityFTI,
        name='Link'
    )
    fti.model_file = "plone.app.contenttypes.schema:link.xml"
    # News Item
    fti = queryUtility(
        IDexterityFTI,
        name='News Item'
    )
    fti.model_file = "plone.app.contenttypes.schema:news_item.xml"


def enable_collection_behavior(context):
    """Enable collection behavior on Collection."""

    fti = queryUtility(
        IDexterityFTI,
        name='Collection'
    )
    behavior = 'plone.app.contenttypes.behaviors.collection.ICollection'
    if behavior in fti.behaviors:
        return
    behaviors = list(fti.behaviors)
    behaviors.append(behavior)
    behaviors = tuple(behaviors)
    fti._updateProperty('behaviors', behaviors)


def migrate_to_richtext(context):
    """Update fti's to add RichText behaviors and remove old text-fields."""

    behavior = "plone.app.contenttypes.behaviors.richtext.IRichText"
    types = [
        "Document",
        "News Item",
        "Event",
        "Collection",
    ]
    for type_name in types:
        fti = queryUtility(
            IDexterityFTI,
            name=type_name
        )
        if not fti:
            continue
        if behavior in fti.behaviors:
            continue
        behaviors = list(fti.behaviors)
        behaviors.append(behavior)
        fti._updateProperty('behaviors', tuple(behaviors))


def migrate_album_view(context):
    """Migrate atct_album_view to album_view."""

    # TODO: Don't reload the profile. Only change the settings.
    context.runImportStepFromProfile(
        'profile-plone.app.contenttypes:default',
        'typeinfo',
    )
    catalog = getToolByName(context, 'portal_catalog')
    search = catalog.unrestrictedSearchResults
    for brain in search(portal_type='Folder'):
        obj = brain.getObject()
        current = context.getLayout()
        if current == 'atct_album_view':
            obj.setLayout('album_view')


def enable_shortname_behavior(context):
    """Add IShortName to all types."""

    behavior = 'plone.app.dexterity.behaviors.id.IShortName'
    for type_id in DEFAULT_TYPES:
        fti = queryUtility(
            IDexterityFTI,
            name=type_id
        )
        if fti is None:
            continue

        if behavior in fti.behaviors:
            continue
        behaviors = list(fti.behaviors)
        behaviors.append(behavior)
        behaviors = tuple(behaviors)
        fti._updateProperty('behaviors', behaviors)


def use_new_view_names(context):
    """Migrate old view names to new view names."""

    # TODO: Don't reload the profile. Only change the settings.
    context.runImportStepFromProfile(
        'profile-plone.app.contenttypes:default',
        'typeinfo',
    )
    catalog = getToolByName(context, 'portal_catalog')
    search = catalog.unrestrictedSearchResults

    def _fixup(portal_type, view_map):
        for brain in search(portal_type=portal_type):
            obj = brain.getObject()
            current = context.getLayout()
            if current in view_map.keys():
                obj.setLayout(view_map[current])
                logger.info("Set view to {} for {}".format(
                    view_map[current], obj.absolute_url()
                ))

    folder_view_map = {  # OLD : NEW
        'folder_listing': 'listing_view',
        'folder_full_view': 'full_view',
        'folder_summary_view': 'summary_view',
        'folder_tabular_view': 'tabular_view',
        'folder_album_view': 'album_view',
        'atct_album_view': 'album_view',
    }
    collection_view_map = {  # OLD : NEW
        'view': 'listing_view',
        'standard_view': 'listing_view',
        'collection_view': 'listing_view',
        'all_content': 'full_view',
        'thumbnail_view': 'album_view',
    }
    _fixup('Folder', folder_view_map)
    _fixup('Plone Site', folder_view_map)
    _fixup('Collection', collection_view_map)
