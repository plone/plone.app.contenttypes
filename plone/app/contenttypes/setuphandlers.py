# -*- coding: utf-8 -*-
from zope.component import (
    getUtility, queryUtility,
    getMultiAdapter, queryMultiAdapter,
    )
from zope.component.hooks import getSite
from zope.container.interfaces import INameChooser
from zope.i18n.interfaces import ITranslationDomain
from zope.i18n.locales import locales
from Acquisition import aq_base, aq_inner
from AccessControl import Unauthorized
from plone.i18n.normalizer.interfaces import IURLNormalizer
from plone.dexterity.utils import createContent
from plone.dexterity.fti import IDexterityFTI
from plone.portlets.interfaces import (
    ILocalPortletAssignmentManager, IPortletManager,)

from Products.PythonScripts.PythonScript import PythonScript
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import bodyfinder
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.Portal import member_indexhtml


def _publish(content):
    """Publish the object if it hasn't been published."""
    portal_workflow = getToolByName(getSite(), "portal_workflow")
    if portal_workflow.getInfoFor(content, 'review_state') != 'published':
        portal_workflow.doActionFor(content, 'publish')
        return True
    return False

def _translate(name, target_language, default=u''):
    """Simple function to tranlate a string."""
    result = None
    if target_language != 'en':
        util = queryUtility(ITranslationDomain, 'plonefrontpage')
        if util is not None:
            result = util.translate(name, target_language=target_language,
                                    default=default)
    return result and result or default

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

def _get_locales_info(portal):
    language = portal.Language()
    parts = (language.split('-') + [None, None])[:3]
    locale = locales.getLocale(*parts)

    # If we get a territory, we enable the combined language codes
    if locale.id.territory:
        return locale.id.language +'_'+ locale.id.territory, True, locale
    
    return locale.id.language, False, locale

def _set_language_settings(portal, uses_combined_lanagage):
    """Set the portals language settings from the given lanage codes."""
    language = portal.Language()
    portal_languages = getToolByName(portal, 'portal_languages')
    portal_languages.manage_setLanguageSettings(
        language,
        [language],
        setUseCombinedLanguageCodes=uses_combined_lanagage,
        startNeutral=False)

# ??? Why do we only do this calendar setup when content is created?
def _setup_calendar(locale):
    """Set the calendar's date system to reflect the default locale"""
    gregorian_calendar = locale.dates.calendars.get(u'gregorian', None)
    portal_calendar = getToolByName(getSite(), "portal_calendar", None)
    if portal_calendar is not None:
        first = 6
        if gregorian_calendar is not None:
            first = gregorian_calendar.week.get('firstDay', None)
            # on the locale object we have: mon : 1 ... sun : 7
            # on the calendar tool we have: mon : 0 ... sun : 6
            if first is not None:
                first = first - 1
        portal_calendar.firstweekday = first

def _setup_visible_ids(target_language, locale):
    portal_properties = getToolByName(getSite(), 'portal_properties')
    site_properties = portal_properties.site_properties

    # See if we have a URL normalizer
    normalizer = queryUtility(IURLNormalizer, name=target_language)
    if normalizer is None:
        normalizer = queryUtility(IURLNormalizer, name=target_language)

    # If we get a script other than Latn we enable visible_ids
    if locale.id.script is not None:
        if locale.id.script.lower() != 'latn':
            site_properties.visible_ids = True

    # If we have a normalizer it is safe to disable the visible ids
    if normalizer is not None:
        site_properties.visible_ids = False

def importContent(context):
    """Import base content into the Plone site."""
    portal = context.getSite()
    # Because the portal doesn't implement __contains__?
    existing_content = portal.keys()
    target_language, is_combined_language, locale = _get_locales_info(portal)
    request = getattr(portal, 'REQUEST', None)

    # Set up Language specific information
    _set_language_settings(portal, is_combined_language)
    _setup_calendar(locale)
    _setup_visible_ids(target_language, locale)

    # TODO Content translations

    # The front-page
    frontpage_id = 'front-page'
    if frontpage_id not in existing_content:
        title = _translate(u'front-title', target_language, u"Welcome to Plone")
        description = _translate(u'front-description', target_language,
                                 u"Congratulations! You have successfully installed Plone.")
        content = createContent('Document', id=frontpage_id,
                                title=title,
                                description=description,
                                )
        content = addContentToContainer(portal, content)

        # TODO front-page text
        # TODO Enable presentation mode
        ##fp.setPresentation(True)

        portal.setDefaultPage('front-page')
        _publish(content)
        content.reindexObject()

    # News topic
    news_id = 'news'
    if news_id not in existing_content:
        title = _translate(u'news-title', target_language, u'News')
        description = _translate(u'news-description', target_language,
                                 u'Site News')
        allowed_types = ['News Item']
        container = createContent('Folder', id=news_id,
                                  title=title,
                                  description=description)
        container = addContentToContainer(portal, container)
        _createObjectByType('Collection', container,
                            id='aggregator', title=title,
                            description=description)
        aggregator = container['aggregator']

        # Set the content-types that can be added to this container.
        # FIXME The following 3 lines
        ##container.setConstrainTypesMode(constraintypes.ENABLED)
        ##container.setLocallyAllowedTypes(allowed_types)
        ##container.setImmediatelyAddableTypes(allowed_types)

        container.setOrdering('unordered')
        container.setDefaultPage('aggregator')
        _publish(container)

        # Set the Collection criteria.
        #: Sort on the Effective date
        aggregator.sort_on = u'effective'
        aggregator.reverse_sort = True
        #: Query by Type and Review State
        aggregator.query = [
            {'i': u'portal_type',
             'o': u'plone.app.querystring.operation.selection.is',
             'v': [u'News Item'],
             },
            {'i': u'review_state',
             'o': u'plone.app.querystring.operation.selection.is',
             'v': [u'published'],
             },
            ]
        aggregator.setLayout('summary_view')

        _publish(aggregator)

    # Events topic
    events_id = 'events'
    if events_id not in existing_content:
        title = _translate(u'events-title', target_language, u'Events')
        description = _translate(u'events-description', target_language,
                                 u'Site Events')
        allowed_types = ['Event']
        container = createContent('Folder', id=events_id,
                                  title=title,
                                  description=description)
        container = addContentToContainer(portal, container)
        _createObjectByType('Collection', container,
                            id='aggregator', title=title,
                            description=description)
        aggregator = container['aggregator']

        # Set the content-types that can be added to this container.
        # FIXME The following 3 lines
        ##container.setConstrainTypesMode(constraintypes.ENABLED)
        ##container.setLocallyAllowedTypes(allowed_types)
        ##container.setImmediatelyAddableTypes(allowed_types)

        container.setOrdering('unordered')
        container.setDefaultPage('aggregator')
        _publish(container)

        # Set up the collection
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
        title = _translate(u'members-title', target_language, u'Users')
        description = _translate(u'members-description', target_language,
                                 u"Site Users")
        container = createContent('Folder', id=members_id,
                                  title=title,
                                  description=description)
        container = addContentToContainer(portal, container)
        container.setOrdering('unordered')
        container.reindexObject()
        _publish(container)

        # add index_html to Members area
        if 'index_html' not in container:
            container._setObject('index_html', PythonScript('index_html'))
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
