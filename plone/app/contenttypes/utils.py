from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityFTI
from plone.folder.interfaces import IOrdering
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base
from Products.CMFCore.utils import getToolByName
from zExceptions import NotFound
from zope.component import queryUtility
from zope.interface import alsoProvides

import importlib
import logging


logger = logging.getLogger(__name__)


DEFAULT_TYPES = [
    "Collection",
    "Document",
    "Event",
    "File",
    "Folder",
    "Image",
    "Link",
    "News Item",
]


def replace_link_variables_by_paths(context, url):
    """Take an `url` and replace the variables "${navigation_root_url}" and
    "${portal_url}" by the corresponding paths. `context` is the acquisition
    context.
    """
    if not url:
        return url

    portal_state = context.restrictedTraverse("@@plone_portal_state")

    if "${navigation_root_url}" in url:
        url = _replace_variable_by_path(
            url, "${navigation_root_url}", portal_state.navigation_root()
        )

    if "${portal_url}" in url:
        url = _replace_variable_by_path(url, "${portal_url}", portal_state.portal())

    return url


def _replace_variable_by_path(url, variable, obj):
    path = "/".join(obj.getPhysicalPath())
    return url.replace(variable, path)


def get_old_class_name_string(obj):
    """Returns the current class name string."""
    return f"{obj.__module__}.{obj.__class__.__name__}"


def get_portal_type_name_string(obj):
    """Returns the klass-attribute of the fti."""
    fti = queryUtility(IDexterityFTI, name=obj.portal_type)
    if not fti:
        return False
    return fti.klass


def migrate_base_class_to_new_class(
    obj,
    indexes=None,
    old_class_name="",
    new_class_name="",
    migrate_to_folderish=False,
):
    if indexes is None:
        indexes = ["is_folderish", "object_provides"]
    if not old_class_name:
        old_class_name = get_old_class_name_string(obj)
    if not new_class_name:
        new_class_name = get_portal_type_name_string(obj)
        if not new_class_name:
            logger.warning(f"The type {obj.portal_type} has no fti!")
            return False

    was_item = not isinstance(obj, BTreeFolder2Base)
    if old_class_name != new_class_name:
        obj_id = obj.getId()
        module_name, class_name = new_class_name.rsplit(".", 1)
        module = importlib.import_module(module_name)
        new_class = getattr(module, class_name)

        # update obj class
        parent = obj.__parent__
        parent._delOb(obj_id)
        obj.__class__ = new_class
        parent._setOb(obj_id, obj)

    is_container = isinstance(obj, BTreeFolder2Base)

    if was_item and is_container or migrate_to_folderish and is_container:
        alsoProvides(obj, IOrdering)
        #  If Itemish becomes Folderish we have to update obj _tree
        BTreeFolder2Base._initBTrees(obj)

    # reindex
    obj.reindexObject(indexes)

    return True


def list_of_objects_with_changed_base_class(context):
    catalog = getToolByName(context, "portal_catalog")
    for brain in catalog(object_provides=IDexterityContent.__identifier__):
        try:
            obj = brain.getObject()
        except (KeyError, NotFound):
            logger.warn(f"Object {brain.getPath()} not found")
            continue
        if get_portal_type_name_string(obj) != get_old_class_name_string(obj):
            yield obj


def changed_base_classes(context):
    """Returns dict of current and new class names ."""
    results = {}
    for obj in list_of_objects_with_changed_base_class(context):
        current_class_name = get_old_class_name_string(obj)
        new_class_name = get_portal_type_name_string(obj)
        if current_class_name not in results:
            results[current_class_name] = {
                "old": current_class_name,
                "new": new_class_name,
                "amount": 1,
            }
        else:
            results[current_class_name]["amount"] += 1
    return results
