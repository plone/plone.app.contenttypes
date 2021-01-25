# -*- coding: utf-8 -*-
from Acquisition import aq_base
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from copy import deepcopy
from plone.app.contentrules.api import assign_rule
from plone.app.contenttypes.behaviors.leadimage import ILeadImage
from plone.app.contenttypes.migration.field_migrators import migrate_imagefield
from plone.app.contenttypes.migration.field_migrators import migrate_simplefield  # noqa
from plone.app.contenttypes.utils import DEFAULT_TYPES
from plone.app.discussion.interfaces import IConversation
from plone.app.linkintegrity.handlers import modifiedArchetype
from plone.app.linkintegrity.handlers import modifiedDexterity
from plone.app.linkintegrity.handlers import referencedRelationship
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.utils import iterSchemataForType
from plone.contentrules.engine.interfaces import IRuleAssignmentManager
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityFTI
from plone.portlets.constants import CONTEXT_BLACKLIST_STATUS_KEY
from plone.portlets.interfaces import ILocalPortletAssignable
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.uuid.interfaces import IUUID
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.interfaces.referenceable import IReferenceable
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import DISCUSSION_ANNOTATION_KEY
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_hasattr
from Products.Five.browser import BrowserView
from Products.GenericSetup.context import DirectoryImportContext
from Products.GenericSetup.utils import importObjects
from z3c.relationfield import RelationValue
from z3c.relationfield.schema import Relation
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zc.relation.interfaces import ICatalog
from zExceptions import NotFound
from zope.annotation.interfaces import IAnnotations
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.component import getSiteManager
from zope.component import getUtility
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import modified

import json
import logging
import os


logger = logging.getLogger(__name__)


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
        try:
            obj = brain.getObject()
        except (KeyError, NotFound):
            continue
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
        raise KeyError('{0} is not one of the default types'.format(type_name))
    portal = getSite()
    tt = getToolByName(portal, 'portal_types')
    fti = tt.getTypeInfo(type_name)
    if IDexterityFTI.providedBy(fti):
        # The dx-type is already installed, so keep it.  But this
        # might be an old dexterity type of Collection, in which case
        # it is better to replace it.
        if type_name != 'Collection':
            return
        if fti.klass == 'plone.app.contenttypes.content.Collection':
            # If the klass is fine, we are happy.
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
    comments = source_annotations.get(DISCUSSION_ANNOTATION_KEY, None)
    if comments is not None:
        target_annotations = IAnnotations(target_object)
        if target_annotations.get(DISCUSSION_ANNOTATION_KEY, None) is not None:
            logger.error('Comments exist on {0}').format(
                target_object.absolute_url())
        # reset the parent before copying
        del comments.__parent__
        copy_of_comments = deepcopy(comments)
        copy_of_comments.__parent__ = target_object
        target_annotations[DISCUSSION_ANNOTATION_KEY] = copy_of_comments

        # Delete comments from the portal where whey were stored temporarily.
        # Comments on the old objects will be removed with the objects.
        if IPloneSiteRoot.providedBy(source_object):
            source_conversation = IConversation(source_object)
            for comment in source_conversation.getComments():
                del source_conversation[comment.comment_id]
            del source_annotations[DISCUSSION_ANNOTATION_KEY]


def copy_contentrules(source_object, target_object):
    """Copy contentrules.
    """
    source_assignable = IRuleAssignmentManager(source_object, None)
    if source_assignable is not None:
        try:
            IRuleAssignmentManager(target_object)
        except TypeError:
            logger.info(
                'Cound not assign contentrules to {0}'.format(
                    target_object.absolute_url()
                )
            )
            return
        rules_storage = getUtility(IRuleStorage)
        available_rules = [r for r in rules_storage]
        for rule_id in source_assignable:
            if rule_id not in available_rules:
                logger.info(
                    'Contentrule {0} does not exist, skip assignment!'.format(
                        rule_id
                    )
                )
                continue
            assign_rule(target_object, rule_id)


def migrate_leadimage(source_object, target_object):
    """ Migrate images added using collective.contentleadimage to the
    ILeadImage-behavior of plone.app.contenttypes if it is enabled.
    """
    OLD_LEADIMAGE_FIELD_NAME = 'leadImage'
    OLD_CAPTION_FIELD_NAME = 'leadImage_caption'
    NEW_LEADIMAGE_FIELD_NAME = 'image'
    NEW_CAPTION_FIELD_NAME = 'image_caption'

    if not source_object.getField(OLD_LEADIMAGE_FIELD_NAME):
        # skip if old content has no field
        return

    if ILeadImage(target_object, None) is None:
        # skip if new content does not have the LeadImage-behavior enabled
        logger.info('Target does not have the behavior "Lead Image" enabled. '
                    'Could not migrate collective.leadimage fields.')
        return

    acc = source_object.getField(
        OLD_LEADIMAGE_FIELD_NAME).getAccessor(source_object)()
    if getattr(acc, 'filename', None) is None:
        # skip if old content has field but has no lead image in the field
        return

    # handle image field
    migrate_imagefield(
        source_object,
        target_object,
        OLD_LEADIMAGE_FIELD_NAME,
        NEW_LEADIMAGE_FIELD_NAME)

    # handle image caption field
    migrate_simplefield(
        source_object,
        target_object,
        OLD_CAPTION_FIELD_NAME,
        NEW_CAPTION_FIELD_NAME)
    logger.info('Migrating contentlead image for {0}.'.format(
        target_object.absolute_url())
    )


def migrate_portlets(src_obj, dst_obj):
    """Copy portlets for all available portletmanagers from one object
    to another.
    Also takes blocked portlet settings into account, keeps hidden portlets
    hidden and skips broken assignments.
    """
    if not ILocalPortletAssignable.providedBy(src_obj) or \
       not ILocalPortletAssignable.providedBy(dst_obj):
        return

    # also take custom portlet managers into account
    managers = [reg.name for reg in getSiteManager().registeredUtilities()
                if reg.provided == IPortletManager]
    # faster, but no custom managers
    # managers = [u'plone.leftcolumn', u'plone.rightcolumn']

    # copy information which categories are hidden for which manager
    blacklist_status = IAnnotations(src_obj).get(
        CONTEXT_BLACKLIST_STATUS_KEY, None)
    if blacklist_status is not None:
        IAnnotations(dst_obj)[CONTEXT_BLACKLIST_STATUS_KEY] = \
            deepcopy(blacklist_status)

    # copy all portlet assignments (visibilty is stored as annotation
    # on the assignments and gets copied here too)
    for manager in managers:
        column = getUtility(IPortletManager, manager)
        mappings = getMultiAdapter((src_obj, column),
                                   IPortletAssignmentMapping)
        for key, assignment in mappings.items():
            # skip possibly broken portlets here
            if not hasattr(assignment, '__Broken_state__'):
                add_portlet(dst_obj, assignment, key, manager)
            else:
                logger.warn(u'skipping broken portlet assignment {0} '
                            'for manager {1}'.format(key, manager))


def store_references(context):
    """Store all references in the portal as a annotation on the portal."""
    all_references = get_all_references(context)
    key = 'ALL_REFERENCES'
    IAnnotations(context)[key] = all_references
    logger.info('Stored {0} relations for later restore.'.format(
        len(all_references))
    )


class ExportAllReferences(BrowserView):
    """Returns all references in the portal as json.
    """

    def __call__(self):
        data = get_all_references(self.context)
        self.request.response.setHeader('Content-type', 'application/json')
        return json.dumps(data)


def get_all_references(context):
    results = []
    # Archetypes
    # Get all data from the reference_catalog if it exists
    reference_catalog = getToolByName(context, REFERENCE_CATALOG, None)
    if reference_catalog is not None:
        for brain in reference_catalog.getAllBrains():
            results.append({
                'from_uuid': brain.sourceUID,
                'to_uuid': brain.targetUID,
                'relationship': brain.relationship,
            })

    # Dexterity
    # Get all data from zc.relation (relation_catalog)
    portal_catalog = getToolByName(context, 'portal_catalog')
    relation_catalog = queryUtility(ICatalog)
    for rel in relation_catalog.findRelations():
        if rel.from_path and rel.to_path:
            from_brain = portal_catalog(path=dict(query=rel.from_path,
                                                  depth=0))
            to_brain = portal_catalog(path=dict(query=rel.to_path, depth=0))
            if len(from_brain) > 0 and len(to_brain) > 0:
                results.append({
                    'from_uuid': from_brain[0].UID,
                    'to_uuid': to_brain[0].UID,
                    'relationship': rel.from_attribute,
                })
    return results


def restore_references(context, relationship_fieldname_mapping=None):
    """Recreate all references stored in an annotation on the context.

    Iterate over the stored references and restore them all according to
    the content-types framework.

    Accepts an optional relationship_fieldname_mapping argument.
    This must be a dictionary with a relationship name as key and fieldname as value.
    For example:
    relationship_fieldname_mapping =  {
        'advisory_contact': 'contact',
        'study_contact': 'contact',
    }
    In this case, old Archetypes content types Advisory and Study both had a
    reference field 'contact' to a content type Contact.
    This relationship was stored under different names for the two contenttypes.
    After migration to Dexterity, the above mapping makes sure the relation is still
    stored on the 'contact' field in both cases.
    The attribute_name of the RelationValue will be the same as this fieldname,
    which is what happens by default when setting relations.

    By default we will also map the 'relatesTo' relation to the 'relatedItems' field.
    This is needed for ATContentTypes.
    """
    if relationship_fieldname_mapping is None:
        relationship_fieldname_mapping = {}
    if 'relatesTo' not in relationship_fieldname_mapping:
        # ATContentTypes used this relation.
        relationship_fieldname_mapping['relatesTo'] = 'relatedItems'
    key = 'ALL_REFERENCES'
    all_references = IAnnotations(context)[key]
    logger.info('Restoring {0} relations.'.format(
        len(all_references))
    )
    for index, ref in enumerate(all_references, 1):
        source_obj = uuidToObject(ref['from_uuid'])
        target_obj = uuidToObject(ref['to_uuid'])
        relationship = ref['relationship']
        if source_obj and target_obj:
            relationship = ref['relationship']
            # By default use the relationship as fieldname.  Fall back to the relationship.
            fieldname = relationship_fieldname_mapping.get(relationship, relationship)
            link_items(context, source_obj, target_obj, relationship, fieldname)
        else:
            logger.warn(
                'Could not restore reference from uid '
                '"{0}" to uid "{1}" on the context: {2}'.format(
                    ref['from_uuid'],
                    ref['to_uuid'],
                    '/'.join(context.getPhysicalPath())
                )
            )
        if not index % 100:
            logger.info('Restoring relations: {}/{}'.format(
                index, len(all_references)))
    del IAnnotations(context)[key]


def link_items(  # noqa
    context,
    source_obj,
    target_obj,
    relationship=None,
    fieldname='relatedItems',
):
    """Add a relation between two content objects.

    This uses the field 'relatedItems' and works for Archetypes and Dexterity.
    By passing a fieldname and a relationship it can be used to create
    arbitrary relations.

    Note: for the relatedItems field, Products.ATContentTypes uses 'relatesTo'
    and plone.app.contenttypes uses 'relatedItems'.
    We switch between these two, based on the source object.
    """
    # relations from AT to DX and from DX to AT are only possible through
    # the referenceable-behavior:
    # plone.app.referenceablebehavior.referenceable.IReferenceable
    drop_msg = """Dropping reference from %s to %s since
    plone.app.referenceablebehavior is not enabled!"""

    if source_obj is target_obj:
        # Thou shalt not relate to yourself.
        return

    if IDexterityContent.providedBy(source_obj):
        source_type = 'DX'
    else:
        source_type = 'AT'

    if IDexterityContent.providedBy(target_obj):
        target_type = 'DX'
    else:
        target_type = 'AT'

    if relationship == referencedRelationship:
        # 'isReferencing' is the relationship for linkintegrity-relations.
        # Linkintegrity-relations should automatically be (re)created by
        # plone.app.linkintegrity.handlers.modifiedDexterity or
        # plone.app.linkintegrity.handlers.modifiedArchetype
        # when a ObjectModifiedEvent is thrown.
        # These relations are only created if the source has a richtext-field
        # with a link to the target and should not be created manually.
        if source_type == 'AT':
            modifiedArchetype(source_obj, None)
        if source_type == 'DX':
            modifiedDexterity(source_obj, None)
        return

    if source_type == 'AT':
        if relationship == 'relatedItems':
            relationship = 'relatesTo'
        # If there is any Archetypes-content there is also the
        # reference_catalog. For a site without AT content this
        # might not be there at all.
        reference_catalog = getToolByName(context, REFERENCE_CATALOG)
        uid_catalog = getToolByName(context, 'uid_catalog')
        if target_type == 'DX' and not is_referenceable(target_obj):
            logger.info(drop_msg % (
                source_obj.absolute_url(), target_obj.absolute_url()))
            return

        # Make sure both objects are properly indexed and referenceable
        # Some objects that werde just created (migrated) are not yet
        # indexed properly.
        source_uid = IUUID(source_obj)
        target_uid = IUUID(target_obj)
        _catalog = uid_catalog._catalog

        if not _catalog.indexes['UID']._index.get(source_uid):
            uid_catalog.catalog_object(source_obj, source_uid)
            modified(source_obj)

        if not _catalog.indexes['UID']._index.get(target_uid):
            uid_catalog.catalog_object(target_obj, target_uid)
            modified(target_obj)

        field = source_obj.getField(fieldname)
        if field is None:
            # we can't migrate if it doesn't actually have the field
            return
        accessor = field.getAccessor(source_obj)
        existing_at_relations = accessor()

        if not isinstance(existing_at_relations, list):
            existing_at_relations = [i for i in existing_at_relations]
        if not existing_at_relations:
            existing_at_relations = []
        if target_obj in existing_at_relations:
            # don't do anything
            return

        target_uid = IUUID(target_obj)
        targetUIDs = [ref.targetUID for ref in reference_catalog.getReferences(
            source_obj, relationship)]
        if target_uid in targetUIDs:
            # Drop relation since the old ones are most likely broken.
            reference_catalog.deleteReference(
                source_obj, target_uid, relationship)

        existing_at_relations.append(target_obj)
        mutator = field.getMutator(source_obj)
        mutator(existing_at_relations)
        modified(source_obj)
        return

    if source_type is 'DX':
        if relationship == 'relatesTo':
            relationship = 'relatedItems'
        if target_type is 'AT' and not is_referenceable(source_obj):
            logger.info(drop_msg % (
                source_obj.absolute_url(), target_obj.absolute_url()))
            return
        # handle dx-relation
        if relationship == 'translationOf':
            # LinguaPlone relations make no sense for Dexterity
            return

        intids = getUtility(IIntIds)
        to_id = intids.getId(target_obj)
        # Before we set the fieldname attribute on the source object,
        # we need to know if this should be a list or a single item.
        # Might be None at the moment.
        # We check the field definition.
        fti = getUtility(IDexterityFTI, name=source_obj.portal_type)
        field = None
        for schema in iterSchemataForType(fti):
            field = schema.get(fieldname, None)
            if field is not None:
                break
        if isinstance(field, RelationList):
            existing_relations = getattr(source_obj, fieldname, [])
            if existing_relations is None:
                existing_relations = []
            else:
                # purge broken relations
                existing_relations = [
                    i for i in existing_relations if i.to_id is not None]
            if to_id not in [i.to_id for i in existing_relations]:
                existing_relations.append(RelationValue(to_id))
                setattr(source_obj, fieldname, existing_relations)
                modified(source_obj)
                return
            return
        elif isinstance(field, (Relation, RelationChoice)):
            setattr(source_obj, fieldname, RelationValue(to_id))
            modified(source_obj)
            return

        # We should never end up here!
        logger.warning('Ignoring unknown fieldname %s when restoring relation %s from %s to %s',
            fieldname, relationship, source_obj.absolute_url(), target_obj.absolute_url())


def is_referenceable(obj):
    """Find out if this object (AT or DX) is referenceable.

    Return True if a obj can be referenced using the reference_catalog used by
    Archetypes-Relations and Linkintegrity.

    Relations using the relation_catalog (zc.relation.interfaces.ICatalog) are
    not covered by this test!
    """
    is_referenceable = False
    if IReferenceable.providedBy(obj) or \
            safe_hasattr(aq_base(obj), 'isReferenceable'):
        is_referenceable = True
    else:
        try:
            # This most likely the case when plone.app.referenceablebehavior
            # is enabled.
            obj = IReferenceable(obj)
            is_referenceable = True
        except TypeError:
            is_referenceable = False
    return is_referenceable
