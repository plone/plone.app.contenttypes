# -*- coding: utf-8 -*-
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base
from Products.CMFCore.utils import getToolByName
from plone.app.contenttypes.utils import DEFAULT_TYPES
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import queryUtility

import logging
logger = logging.getLogger(__name__)

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


def migrate_to_folderish_types(context):
    """Migrate instances to work as containers.

    The base-class for all types except Link, Image and File changed to
    container. This step re-instaciated the _tree of existing instances
    to be useable after the change.
    We only have to reinstanciate the _tree of the objects. We don't need to
    change the class of these objects since it stays the same (only the
    base-class changes). For the same reason we also don't have to re-add the
    objects to their parents.
    See .migration.dxmigration.migrate_base_class_to_new_class for a full
    example of migrating classes.

    We might as well have used:
        migrate_base_class_to_new_class(obj, migrate_to_folderish=True)
    """

    to_migrate = [
        'plone.app.contenttypes.interfaces.ICollection',
        'plone.app.contenttypes.interfaces.IDocument',
        'plone.app.contenttypes.interfaces.IEvent',
        'plone.app.contenttypes.interfaces.INewsItem',
        'plone.app.contenttypes.interfaces.ILink',
    ]
    catalog = getToolByName(context, 'portal_catalog')
    search = catalog.unrestrictedSearchResults
    for iface in to_migrate:
        brains = search(meta_type='Dexterity Item',
                        object_provides=iface)
        if brains:
            logger.info(
                'Switching {0} {1}s from item to container'.format(
                    len(brains), iface.split('.')[-1][1:]))
        for brain in brains:
            obj = brain.getObject()
            if not obj:
                logger.info('No object found at {0}'.format(brain.getPath()))
                continue

            # Since the objs are now folderish update the objects _tree
            # obj is now a instance of BTreeFolder2Base
            BTreeFolder2Base._initBTrees(obj)
            obj.reindexObject(['is_folderish', 'object_provides'])
