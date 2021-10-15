# -*- coding: utf-8 -*-
from plone.app.contenttypes.utils import DEFAULT_TYPES
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFCore.utils import getToolByName
from zope.component import queryUtility
from zope.component.hooks import getSite

import logging


logger = logging.getLogger(name='plone.app.contenttypes upgrade')

LISTING_VIEW_MAPPING = {  # OLD (AT and old DX) : NEW
    'all_content': 'full_view',
    'atct_album_view': 'album_view',
    'atct_topic_view': 'listing_view',
    'collection_view': 'listing_view',
    'folder_album_view': 'album_view',
    'folder_full_view': 'full_view',
    'folder_listing': 'listing_view',
    'folder_listing_view': 'listing_view',
    'folder_summary_view': 'summary_view',
    'folder_tabular_view': 'tabular_view',
    'standard_view': 'listing_view',
    'thumbnail_view': 'album_view',
    'view': 'listing_view',
}


def _brains2objs(brains):
    ''' Generator that takes a brains lazy map and:
    - yields the objects that can be resolved
    - logs the brain that cannot be resolved
    '''
    for brain in brains:
        obj = brain.getObject()
        if obj:
            yield obj
        else:
            logger.warning(
                'Cannot resolve brain %s',
                brain.getPath(),
            )


def update_fti(context):
    """ Schema-files moved into their own folder after 1.0b1
    """
    # Document
    fti = queryUtility(
        IDexterityFTI,
        name='Document'
    )
    fti.model_file = 'plone.app.contenttypes.schema:document.xml'
    # File
    fti = queryUtility(
        IDexterityFTI,
        name='File'
    )
    fti.model_file = 'plone.app.contenttypes.schema:file.xml'
    # Folder
    fti = queryUtility(
        IDexterityFTI,
        name='Folder'
    )
    fti.model_file = 'plone.app.contenttypes.schema:folder.xml'
    # Image
    fti = queryUtility(
        IDexterityFTI,
        name='Image'
    )
    fti.model_file = 'plone.app.contenttypes.schema:image.xml'
    # Link
    fti = queryUtility(
        IDexterityFTI,
        name='Link'
    )
    fti.model_file = 'plone.app.contenttypes.schema:link.xml'
    # News Item
    fti = queryUtility(
        IDexterityFTI,
        name='News Item'
    )
    fti.model_file = 'plone.app.contenttypes.schema:news_item.xml'


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

    behavior = 'plone.app.contenttypes.behaviors.richtext.IRichTextBehavior'
    types = [
        'Document',
        'News Item',
        'Event',
        'Collection',
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
    """That task is now done by use_new_view_names (1103->1104)"""
    pass


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


def use_new_view_names(context, types_to_fix=None):  # noqa
    """Migrate old view names to new view names."""
    # Don't reload the profile. Only change the settings.
    logger.info('Start updating view names...')
    portal = getSite()
    portal_types = getToolByName(portal, 'portal_types')
    if types_to_fix is None:
        types_to_fix = ['Folder', 'Collection', 'Plone Site']
    outdated_methods = [
        'folder_listing',
        'folder_full_view',
        'folder_summary_view',
        'folder_tabular_view',
        'folder_album_view',
        'atct_album_view',
        'standard_view',
        'collection_view',
        'all_content',
        'thumbnail_view',
    ]
    new_methods = [
        'listing_view',
        'summary_view',
        'tabular_view',
        'full_view',
        'album_view',
        'event_listing',
    ]
    for ctype in types_to_fix:
        fti = queryUtility(IDexterityFTI, name=ctype)
        if fti is None and ctype == 'Plone Site':
            fti = portal_types.get(ctype)
        if fti is None:
            return
        view_methods = [i for i in fti.getAvailableViewMethods(None)]
        changed = False
        for method in outdated_methods:
            if method in view_methods:
                view_methods.remove(method)
                changed = True
        for method in new_methods:
            if method not in view_methods:
                view_methods.append(method)
                changed = True
        default_view = fti.default_view
        if default_view in outdated_methods:
            default_view = LISTING_VIEW_MAPPING.get(default_view)
            changed = True
        if changed:
            fti.manage_changeProperties(
                view_methods=tuple(view_methods),
                default_view=default_view,
            )
            logger.info('Updated view_methods for {0}'.format(ctype))

    def _fixup(obj, view_map):
        current = obj.getLayout()
        if current in view_map:
            default_page = obj.getDefaultPage()
            obj.setLayout(view_map[current])
            logger.info('Set view to {0} for {1}'.format(
                view_map[current],
                obj.absolute_url(),
            ))
            if default_page:
                # any defaultPage is switched of by setLayout
                # and needs to set again
                obj.setDefaultPage(default_page)

    catalog = getToolByName(portal, 'portal_catalog')
    search = catalog.unrestrictedSearchResults
    for portal_type in types_to_fix:
        logger.info('Updating view names for {}'.format(portal_type))
        brains = search(portal_type=portal_type)
        objs = _brains2objs(brains)
        for obj in objs:
            _fixup(obj, LISTING_VIEW_MAPPING)
        if portal_type == 'Plone Site':
            _fixup(context, LISTING_VIEW_MAPPING)


def searchabletext_collections(context):
    """Reindex Collections for SearchableText."""
    catalog = getToolByName(context, 'portal_catalog')
    search = catalog.unrestrictedSearchResults
    brains = search(portal_type='Collection')
    objs = _brains2objs(brains)
    for obj in objs:
        obj.reindexObject(idxs=['SearchableText'])


def searchabletext_richtext(context):
    """Reindex rich text types for SearchableText.

    Our SearchableText indexer has been going back and forth between
    taking the raw text or the output, and using the original mimetype
    or the output mimetype.  We are on the third combination now
    (original raw source with original mimetype) so it is time to reindex.

    See https://github.com/plone/Products.CMFPlone/issues/2066
    """
    catalog = getToolByName(context, 'portal_catalog')
    search = catalog.unrestrictedSearchResults
    brains = search(portal_type=['Collection', 'Document', 'News Item'])
    objs = _brains2objs(brains)
    for obj in objs:
        obj.reindexObject(idxs=['SearchableText'])


def update_type_icons(context):
    """Update portal_type icons.

    We want to update two things:

    - the icon_expr property of the portal_type
    - the icon_expr property of the view and edit actions.

    This is for the standard types defined here, plus the Plone Site.

    An earlier version of this upgrade step did this in xml in an upgrade
    profile.  This led to duplicate view and edit actions, because the xml did
    not contain a category for the action.
    A second try with xml still resulted in duplicate view actions,
    and the view and edit actions were invisible.

    Conclusion: if we want to do this in xml, we must specify *all* properties.
    And we do not want this, because these properties may have been changed
    by the user.
    So: we do it in Python.
    """
    types = {
        "Collection": "string:contenttype/collection",
        "Document": "string:contenttype/document",
        "Event": "string:contenttype/event",
        "File": "string:contenttype/file",
        "Folder": "string:contenttype/folder",
        "Image": "string:contenttype/image",
        "Link": "string:contenttype/link",
        "News Item": "string:contenttype/news-item",
        "Plone Site": "string:contenttype/plone",
    }
    view_icon_expr = "string:toolbar-action/view"
    edit_icon_expr = "string:toolbar-action/edit"
    for type_name, icon_expr in types.items():
        fti = queryUtility(IDexterityFTI, name=type_name)
        if not fti:
            continue
        if fti.getProperty("icon_expr") != icon_expr:
            if not fti.hasProperty("icon_expr"):
                fti._setProperty("icon_expr", icon_expr)
            else:
                fti._updateProperty("icon_expr", icon_expr)
            logger.info("Set icon_expr property on FTI %s to %s", type_name, icon_expr)

        # Build up the new actions list.
        new_actions = []
        discarded_actions = []
        found_visible_view = False
        found_visible_edit = False
        changed_icon_expression = False
        for action in fti._actions:
            if not action.category:
                discarded_actions.append(action)
                continue
            if action.category != "object":
                new_actions.append(action)
                continue
            if action.id not in ("view", "edit"):
                new_actions.append(action)
                continue
            # At this point we have id=view/edit and category=object.
            if not action.visible:
                # A previous version of the update may have resulted in
                # an extra, invisible action.
                discarded_actions.append(action)
                continue
            action_icon_expr = action.getIconExpression()
            if action.id == "view":
                found_visible_view = True
                if action_icon_expr != view_icon_expr:
                    # This is what we wanted: change the icon expression.
                    action.setIconExpression(view_icon_expr)
                    changed_icon_expression = True
            elif action.id == "edit":
                found_visible_edit = True
                if action_icon_expr != edit_icon_expr:
                    # This is what we wanted: change the icon expression.
                    action.setIconExpression(edit_icon_expr)
                    changed_icon_expression = True
            new_actions.append(action)
        if not (found_visible_view and found_visible_edit):
            # This is an unexpected situation.
            # If we change something, we might make it worse.
            logger.warning(
                "Did not find both visible view and edit actions for type %s. Not updating type icons.",
                type_name,
            )
            continue
        if not (discarded_actions or changed_icon_expression):
            # no changes needed
            continue
        if discarded_actions:
            logger.info(
                "Removed %d actions without category from FTI %s.",
                len(discarded_actions),
                type_name,
            )
        if changed_icon_expression:
            logger.info(
                "Changed icon expression for view/edit action from FTI %s.",
                type_name,
            )
        fti._actions = tuple(new_actions)
