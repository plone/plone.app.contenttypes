# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode, safe_hasattr
from Products.GenericSetup.context import DirectoryImportContext
from Products.GenericSetup.utils import importObjects
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from copy import deepcopy
from plone.app.contentrules.api import assign_rule
from plone.app.contenttypes.behaviors.leadimage import ILeadImage
from plone.app.contenttypes.utils import DEFAULT_TYPES
from plone.app.discussion.conversation import ANNOTATION_KEY as DISCUSSION_KEY
from plone.app.discussion.interfaces import IConversation
from plone.contentrules.engine.interfaces import IRuleAssignmentManager
from plone.dexterity.interfaces import IDexterityFTI
from plone.namedfile.file import NamedBlobImage
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zope.annotation.interfaces import IAnnotations
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import getSite

import logging
import os
import pkg_resources

logger = logging.getLogger(__name__)

# Is there a multilingual addon?
try:
    pkg_resources.get_distribution('Products.LinguaPlone')
except pkg_resources.DistributionNotFound:
    HAS_MULTILINGUAL = False
else:
    HAS_MULTILINGUAL = True

if not HAS_MULTILINGUAL:
    try:
        pkg_resources.get_distribution('plone.app.multilingual')
    except pkg_resources.DistributionNotFound:
        HAS_MULTILINGUAL = False
    else:
        HAS_MULTILINGUAL = True


def isSchemaExtended(iface):
    """Return a list of fields added by archetypes.schemaextender
    """
    fields = _compareSchemata(iface)
    fields2 = _checkForExtenderInterfaces(iface)
    fields.extend(fields2)
    return [i for i in set(fields)]


def _compareSchemata(interface):
    """Return a list of extended fields by archetypes.schemaextender
    by comparing the real and the default schemata.
    """
    portal = getSite()
    pc = portal.portal_catalog
    brains = pc(object_provides=interface.__identifier__)
    for brain in brains:
        if not brain.meta_type or 'dexterity' in brain.meta_type.lower():
            # There might be DX types with same iface and meta_type than AT
            continue
        obj = brain.getObject()
        real_fields = set(obj.Schema()._names)
        orig_fields = set(obj.schema._names)
        diff = [i for i in real_fields.difference(orig_fields)]
        return diff
    return []


def _checkForExtenderInterfaces(interface):
    """Return whether a specific content type interface
    is extended by archetypes.schemaextender or not.
    """
    sm = getGlobalSiteManager()
    extender_interfaces = [
        ISchemaExtender,
        ISchemaModifier,
        IBrowserLayerAwareExtender,
        IOrderableSchemaExtender,
    ]
    # We have a few possible interfaces to test
    # here, so get all the interfaces that
    # are for the given content type first
    registrations = \
        [a for a in sm.registeredAdapters() if interface in a.required]
    for adapter in registrations:
        if adapter.provided in extender_interfaces:
            fields = getattr(adapter.factory(None), 'fields', [])
            return [field.getName() for field in fields]
    return []


def installTypeIfNeeded(type_name):
    """Make sure the dexterity-fti is already installed.
    If not we create a empty dexterity fti and load the
    information from the fti in the profile.
    """
    if type_name not in DEFAULT_TYPES:
        raise KeyError("%s is not one of the default types" % type_name)
    portal = getSite()
    tt = getToolByName(portal, 'portal_types')
    fti = tt.getTypeInfo(type_name)
    if IDexterityFTI.providedBy(fti):
        # the dx-type is already installed
        return
    if fti:
        tt.manage_delObjects(type_name)
    tt.manage_addTypeInformation('Dexterity FTI', id=type_name)
    dx_fti = tt.getTypeInfo(type_name)
    ps = getToolByName(portal, 'portal_setup')
    profile_info = ps.getProfileInfo('profile-plone.app.contenttypes:default')
    profile_path = os.path.join(profile_info['path'])
    environ = DirectoryImportContext(ps, profile_path)
    parent_path = 'types/'
    importObjects(dx_fti, parent_path, environ)


def add_portlet(context, assignment, portlet_key, columnName):
    column = getUtility(IPortletManager, columnName)
    assignmentmapping = getMultiAdapter((context, column),
                                        IPortletAssignmentMapping)
    assignmentmapping[portlet_key] = assignment


def move_comments(source_object, target_object):
    """Move comments by copying the annotation to the target
    and then removing the comments from the source (not the annotation).
    """
    source_annotations = IAnnotations(source_object)
    comments = source_annotations.get(DISCUSSION_KEY, None)
    if comments is not None:
        target_annotations = IAnnotations(target_object)
        if target_annotations.get(DISCUSSION_KEY, None) is not None:
            logger.error('Comments exist on {0}').format(
                target_object.absolute_url())
        target_annotations[DISCUSSION_KEY] = deepcopy(comments)

        # Delete comments from the portal where wthey were stored temporarily.
        # Comments on the old objects will be removed with the objects.
        if IPloneSiteRoot.providedBy(source_object):
            source_conversation = IConversation(source_object)
            for comment in source_conversation.getComments():
                del source_conversation[comment.comment_id]
            del source_annotations[DISCUSSION_KEY]


def copy_contentrules(source_object, target_object):
    """Copy contentrules.
    """
    source_assignable = IRuleAssignmentManager(source_object, None)
    if source_assignable is not None:
        try:
            IRuleAssignmentManager(target_object)
        except TypeError:
            logger.info("Cound not assign contentrules to {0}".format(
                target_object.absolute_url()))
            return
        for rule_id in source_assignable:
            assign_rule(target_object, rule_id)


def migrate_leadimage(source_object, target_object):
    """ Migrate images added using collective.contentleadimage to the
    ILeadImage-behavior of plone.app.contenttypes if it is enabled.
    """
    OLD_LEADIMAGE_FIELD_NAME = 'leadImage'
    OLD_CAPTION_FIELD_NAME = 'leadImage_caption'
    NEW_LEADIMAGE_FIELD_NAME = 'image'
    NEW_CAPTION_FIELD_NAME = 'image_caption'

    old_leadimage_field = source_object.getField(OLD_LEADIMAGE_FIELD_NAME)
    if not old_leadimage_field:
        # skip if old content has no field
        return

    if ILeadImage(target_object, None) is None:
        # skip if new content does not have the LeadImage-behavior enabled
        logger.info("Target does not have the behavior 'Lead Image' enabled. "
                    "Could not migrate collective.leadimage fields.")
        return

    old_image = old_leadimage_field.get(source_object)
    if not old_image:
        # skip if image-field is empty
        return

    filename = safe_unicode(old_image.filename)
    old_image_data = old_image.data
    if safe_hasattr(old_image_data, 'data'):
        # handle relstorage
        old_image_data = old_image_data.data

    # construct the new image
    namedblobimage = NamedBlobImage(data=old_image_data,
                                    filename=filename)

    # set new field on destination object
    setattr(target_object, NEW_LEADIMAGE_FIELD_NAME, namedblobimage)

    # handle image caption field
    caption_field = source_object.getField(OLD_CAPTION_FIELD_NAME, None)
    if caption_field:
        setattr(target_object,
                (NEW_CAPTION_FIELD_NAME),
                safe_unicode(caption_field.get(source_object)))
    logger.info("Migrating contentlead image %s" % filename)
