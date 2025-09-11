from plone.dexterity.interfaces import IDexterityFTI
from zope.component import queryUtility

import logging


logger = logging.getLogger(name="plone.app.contenttypes upgrade")


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
