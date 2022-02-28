from plone.dexterity.interfaces import IDexterityFTI
from zope.component import queryUtility
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base
from zope.interface import alsoProvides
from plone.folder.interfaces import IOrdering
from Products.CMFCore.utils import getToolByName
from zExceptions import NotFound
from plone.dexterity.interfaces import IDexterityContent

import importlib
import logging

logger = logging.getLogger(__name__)


DEFAULT_TYPES = [
    'Collection',
    'Document',
    'Event',
    'File',
    'Folder',
    'Image',
    'Link',
    'News Item',
]


def replace_link_variables_by_paths(context, url):
    """Take an `url` and replace the variables "${navigation_root_url}" and
    "${portal_url}" by the corresponding paths. `context` is the acquisition
    context.
    """
    if not url:
        return url

    portal_state = context.restrictedTraverse('@@plone_portal_state')

    if '${navigation_root_url}' in url:
        url = _replace_variable_by_path(
            url,
            '${navigation_root_url}',
            portal_state.navigation_root()
        )

    if '${portal_url}' in url:
        url = _replace_variable_by_path(
            url,
            '${portal_url}',
            portal_state.portal()
        )

    return url


def _replace_variable_by_path(url, variable, obj):
    path = obj.absolute_url()
    return url.replace(variable, path)


def get_old_class_name_string(obj):
    """Returns the current class name string."""
    return '{0}.{1}'.format(obj.__module__, obj.__class__.__name__)


def get_portal_type_name_string(obj):
    """Returns the klass-attribute of the fti."""
    fti = queryUtility(IDexterityFTI, name=obj.portal_type)
    print(fti.klass)
    print(fti.id)
    if not fti:
        return False
    return fti.klass


def migrate_base_class_to_new_class(obj,
                                    indexes=None,
                                    old_class_name='',
                                    new_class_name='',
                                    migrate_to_folderish=False,
                                    ):
    if indexes is None:
        indexes = ['is_folderish', 'object_provides']
    if not old_class_name:
        old_class_name = get_old_class_name_string(obj)
    if not new_class_name:
        new_class_name = get_portal_type_name_string(obj)
        if not new_class_name:
            logger.warning(
                'The type {0} has no fti!'.format(obj.portal_type))
            return False

    was_item = not isinstance(obj, BTreeFolder2Base)
    if old_class_name != new_class_name:
        obj_id = obj.getId()
        module_name, class_name = new_class_name.rsplit('.', 1)
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
    catalog = getToolByName(context, 'portal_catalog')
    for brain in catalog(object_provides=IDexterityContent.__identifier__):
        try:
            obj = brain.getObject()
        except (KeyError, NotFound):
            logger.warn('Object {0} not found'.format(brain.getPath()))
            continue
        if get_portal_type_name_string(obj) != get_old_class_name_string(obj):
            yield obj


def list_of_changed_base_class_names(context):
    """Returns list of class names that are not longer in portal_types."""
    changed_base_class_names = {}
    for obj in list_of_objects_with_changed_base_class(context):
        changed_base_class_name = get_old_class_name_string(obj)
        if changed_base_class_name not in changed_base_class_names:
            changed_base_class_names[changed_base_class_name] = 1
        else:
            changed_base_class_names[changed_base_class_name] += 1
    return changed_base_class_names
