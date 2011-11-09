# -*- coding: utf-8 -*-
from zope.component import getUtility, queryUtility, getMultiAdapter
from zope.component.hooks import getSite
from zope.container.interfaces import INameChooser
from Acquisition import aq_base, aq_inner
from AccessControl import Unauthorized
from plone.dexterity.utils import createContent
from plone.dexterity.fti import IDexterityFTI
from plone.portlets.interfaces import (
    ILocalPortletAssignmentManager, IPortletManager,)

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.Portal import member_indexhtml


def _publish(content):
    """Publish the object if it hasn't been published."""
    portal_workflow = getToolByName(getSite(), "portal_workflow")
    if portal_workflow.getInfoFor(content, 'review_state') != 'published':
        portal_workflow.doActionFor(content, 'publish')
        return True
    return False

def addContentToContainer(container, object, checkConstraints=True):
    """Copy of plone.dexterity.util.addContentToContainer.
    Modified to check the existing Id on the object before paving over it.
    """
    if not hasattr(aq_base(object), "portal_type"):
        raise ValueError("object must have its portal_type set")

    container = aq_inner(container)
    if checkConstraints:
        container_fti = container.getTypeInfo()

        fti = getUtility(IDexterityFTI, name=object.portal_type)
        if not fti.isConstructionAllowed(container):
            raise Unauthorized("Cannot create %s" % object.portal_type)
        
        if container_fti is not None and not container_fti.allowType(object.portal_type):
            raise ValueError("Disallowed subobject type: %s" % object.portal_type)

    chooser = INameChooser(container)
    if hasattr(object, 'id') and chooser.checkName(object.id, object):
        name = object.id
    else:
        name = INameChooser(container).chooseName(None, object)
        object.id = name

    newName = container._setObject(name, object)
    return container._getOb(newName)

def importContent(context):
    """Import base content into the Plone site."""
    portal = context.getSite()
    # Because the portal doesn't implement __contains__?
    existing_content = portal.keys()
    request = getattr(portal, 'REQUEST', None)

    # TODO Content translations

    # The front-page
    frontpage_id = 'front-page'
    if frontpage_id not in existing_content:
        title = u"Welcome to Plone"
        description = u"Congratulations! You have successfully installed Plone."
        content = createContent('Document', id=frontpage_id,
                                title=title,
                                description=description)
        content = addContentToContainer(portal, content)
        # TODO front-page text
        # TODO Show off presentation mode
        ##fp.setPresentation(True)

        portal.setDefaultPage('front-page')
        _publish(content)
        content.reindexObject()

    # News topic
    news_id = 'news'
    if news_id not in existing_content:
        title = 'News'
        description = 'Site News'
        allowed_types = ['News Item']
        container = createContent('Folder', id=news_id,
                                  title=title,
                                  description=description)
        container = addContentToContainer(portal, container)
        _createObjectByType('Collection', container,
                            id='aggregator', title=title,
                            description=description)
        aggregator = container['aggregator']
        container.setOrdering('unordered')
        # FIXME The following 3 lines
        ##container.setConstrainTypesMode(constraintypes.ENABLED)
        ##container.setLocallyAllowedTypes(allowed_types)
        ##container.setImmediatelyAddableTypes(allowed_types)
        container.setDefaultPage('aggregator')
        _publish(container)

        # TODO Set the Collection criteria.
        # type_crit = topic.addCriterion('Type', 'ATPortalTypeCriterion')
        # type_crit.setValue('News Item')
        # topic.addCriterion('created', 'ATSortCriterion')
        # state_crit = topic.addCriterion('review_state', 'ATSimpleStringCriterion')
        # state_crit.setValue('published')
        # topic.setSortCriterion('effective', True)
        # topic.setLayout('folder_summary_view')

        _publish(aggregator)

    # Events topic
    events_id = 'events'
    if events_id not in existing_content:
        title = 'Events'
        description = 'Site Events'
        allowed_types = ['Event']
        container = createContent('Folder', id=news_id,
                                  title=title,
                                  description=description)
        container = addContentToContainer(portal, container)
        _createObjectByType('Collection', container,
                            id='aggregator', title=title,
                            description=description)
        aggregator = container['aggregator']
        container.setOrdering('unordered')
        # FIXME The following 3 lines
        ##container.setConstrainTypesMode(constraintypes.ENABLED)
        ##container.setLocallyAllowedTypes(allowed_types)
        ##container.setImmediatelyAddableTypes(allowed_types)
        container.setDefaultPage('aggregator')
        _publish(container)

        # type_crit = topic.addCriterion('Type', 'ATPortalTypeCriterion')
        # type_crit.setValue('Event')
        # topic.addCriterion('start', 'ATSortCriterion')
        # state_crit = topic.addCriterion('review_state', 'ATSimpleStringCriterion')
        # state_crit.setValue('published')
        # date_crit = topic.addCriterion('start', 'ATFriendlyDateCriteria')
        # # Set date reference to now
        # date_crit.setValue(0)
        # # Only take events in the future
        # date_crit.setDateRange('+') # This is irrelevant when the date is now
        # date_crit.setOperation('more')
        _publish(aggregator)

    # configure Members folder
    members_id = 'Members'
    if members_id not in existing_content:
        title = 'Users'
        description = "Site Users"
        container = createContent('Folder', id=members_id,
                                  title=title,
                                  description=description)
        container = addContentToContainer(portal, container)
        container.setOrdering('unordered')
        container.reindexObject()
        _publish(container)

        # add index_html to Members area
        if 'index_html' not in container:
            addPy = container.manage_addProduct['PythonScripts'].manage_addPythonScript
            addPy('index_html')
            index_html = getattr(container, 'index_html')
            index_html.write(member_indexhtml)
            index_html.ZPythonScript_setTitle('User Search')

        # Block all right column portlets by default
        manager = queryUtility(IPortletManager, name='plone.rightcolumn')
        if manager is not None:
            assignable = getMultiAdapter((container, manager), ILocalPortletAssignmentManager)
            assignable.setBlacklistStatus('context', True)
            assignable.setBlacklistStatus('group', True)
            assignable.setBlacklistStatus('content_type', True)
