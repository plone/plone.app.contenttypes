# -*- coding: utf-8 -*-
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
    """Enable collection behavior on Collection.
    """
    fti = queryUtility(
        IDexterityFTI,
        name='Collection'
    )
    if not fti:
        return
    behavior = 'plone.app.contenttypes.behaviors.collection.ICollection'
    if behavior in fti.behaviors:
        return
    behaviors = fti.behaviors + (behavior,)
    fti._updateProperty('behaviors', behaviors)


def migrate_to_richtext(context):
    """update fti's to add RichText behaviors and remove old text-fields"""

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
            return
        behaviors = fti.behaviors + (behavior,)
        fti._updateProperty('behaviors', behaviors)
        # the mode-file is automatically reloaded?
