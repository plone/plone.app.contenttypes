# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.app.contenttypes.utils import DEFAULT_TYPES
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import queryUtility


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

    # TODO: Don't reload the profile. Only change the settings.
    context.runImportStepFromProfile(
        'profile-plone.app.contenttypes:default',
        'typeinfo',
    )


def migrate_album_view(context):
    """Migrate atct_album_view to folder_album_view."""

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
            obj.setLayout('folder_album_view')


def enable_shortname_behavior(context):
    """Add IShortName to all types."""

    for type_id in DEFAULT_TYPES:
        fti = queryUtility(
            IDexterityFTI,
            name=type_id
        )
        if fti is None:
            continue

        behavior = 'plone.app.dexterity.behaviors.id.IShortName'
        if behavior in fti.behaviors:
            return
        behaviors = list(fti.behaviors)
        behaviors.append(behavior)
        behaviors = tuple(behaviors)
        fti._updateProperty('behaviors', behaviors)
