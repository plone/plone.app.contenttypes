# -*- coding: utf-8 -*-
from plone.app.contenttypes.migration.dxmigration import DXOldEventMigrator
from plone.app.contenttypes.migration.dxmigration import migrate
from plone.app.upgrade.utils import loadMigrationProfile
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import queryUtility
from zope.component.hooks import getSite


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
    # Document
    fti = queryUtility(
        IDexterityFTI,
        name='Collection'
    )
    behavior = 'plone.app.contenttypes.behaviors.collection.ICollection'
    if behavior in fti.behaviors:
        return
    new = list(fti.behaviors)
    new.append(behavior)
    fti.behaviors = tuple(new)
    if fti.schema == 'plone.app.contenttypes.interfaces.ICollection':
        fti.schema = None


def migrate_to_pa_event(context):
    loadMigrationProfile(context, 'profile-plone.app.event:default')
    # Re-import types to get newest Event type
    context.runImportStepFromProfile(
        'profile-plone.app.contenttypes:default',
        'typeinfo',
    )
    portal = getSite()
    migrate(portal, DXOldEventMigrator)
