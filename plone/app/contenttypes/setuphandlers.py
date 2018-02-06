# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Acquisition import aq_base
from Acquisition import aq_inner
from plone.app.contenttypes.upgrades import use_new_view_names
from plone.app.dexterity.behaviors import constrains
from plone.app.textfield.value import RichTextValue
from plone.dexterity.fti import IDexterityFTI
from plone.dexterity.utils import createContent
from plone.i18n.normalizer.interfaces import IURLNormalizer
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletManager
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import INonInstallable
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import bodyfinder
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.container.interfaces import INameChooser
from zope.i18n.interfaces import ITranslationDomain
from zope.i18n.locales import locales
from zope.i18n.locales.provider import LoadLocaleError
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """
        Prevents all profiles but 'plone-content' from showing up in the
        profile list when creating a Plone site.
        """
        return [
            u'plone.app.contenttypes:uninstall',
            u'plone.app.contenttypes:default',
        ]


def _publish(content):
    """Publish the object if it hasn't been published."""
    portal_workflow = getToolByName(getSite(), 'portal_workflow')
    if portal_workflow.getInfoFor(content, 'review_state') != 'published':
        portal_workflow.doActionFor(content, 'publish')
        return True
    return False


def _translate(name, target_language, default=u''):
    """Simple function to translate a string."""
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
    if not hasattr(aq_base(object), 'portal_type'):
        raise ValueError('object must have its portal_type set')

    container = aq_inner(container)
    if checkConstraints:
        container_fti = container.getTypeInfo()

        fti = getUtility(IDexterityFTI, name=object.portal_type)
        if not fti.isConstructionAllowed(container):
            raise Unauthorized('Cannot create {0}'.format(object.portal_type))

        if container_fti is not None and \
                not container_fti.allowType(object.portal_type):
            raise ValueError(
                'Disallowed subobject type: {0}'.format(object.portal_type)
            )

    chooser = INameChooser(container)
    if hasattr(object, 'id') and chooser.checkName(object.id, object):
        name = object.id
    else:
        name = INameChooser(container).chooseName(None, object)
        object.id = name

    newName = container._setObject(name, object)
    return container._getOb(newName)


def _get_locales_info(portal):
    reg = queryUtility(IRegistry, context=portal)
    language = reg['plone.default_language']
    parts = (language.split('-') + [None, None])[:3]

    try:
        locale = locales.getLocale(*parts)

        # If we get a territory, we enable the combined language codes
        if locale.id.territory:
            return locale.id.language + '_' + locale.id.territory, True, locale
        return locale.id.language, False, locale
    except LoadLocaleError:
        # default to *some* language so we don't error out
        return language, False, locales.getLocale('en')


def _setup_calendar(portal, locale):
    """Set the calendar's date system to reflect the default locale"""
    gregorian_calendar = locale.dates.calendars.get(u'gregorian', None)
    portal_calendar = getToolByName(portal, 'portal_calendar', None)
    if portal_calendar is not None:
        first = 6
        if gregorian_calendar is not None:
            first = gregorian_calendar.week.get('firstDay', None)
            # on the locale object we have: mon : 1 ... sun : 7
            # on the calendar tool we have: mon : 0 ... sun : 6
            if first is not None:
                first = first - 1
        portal_calendar.firstweekday = first


def _setup_visible_ids(portal, target_language, locale):
    portal_properties = getToolByName(portal, 'portal_properties')
    site_properties = portal_properties.site_properties

    # See if we have a URL normalizer
    normalizer = queryUtility(IURLNormalizer, name=target_language)
    if normalizer is None:
        normalizer = queryUtility(IURLNormalizer)

    # If we get a script other than Latn we enable visible_ids
    if locale.id.script is not None:
        if locale.id.script.lower() != 'latn':
            site_properties.visible_ids = True

    # If we have a normalizer it is safe to disable the visible ids
    if normalizer is not None:
        site_properties.visible_ids = False


def _setup_constrains(container, allowed_types):
    behavior = ISelectableConstrainTypes(container)
    behavior.setConstrainTypesMode(constrains.ENABLED)
    behavior.setImmediatelyAddableTypes(allowed_types)
    return True


def create_frontpage(portal, target_language):
    frontpage_id = 'front-page'

    if frontpage_id not in portal.keys():
        title = _translate(
            u'front-title',
            target_language,
            u'Welcome to Plone'
        )
        description = _translate(
            u'front-description', target_language,
            u'Congratulations! You have successfully installed Plone.'
        )
        content = createContent(
            'Document', id=frontpage_id,
            title=title,
            description=description,
            language=target_language.replace('_', '-').lower())
        content = addContentToContainer(portal, content)
        front_text = None
        if target_language != 'en':
            util = queryUtility(ITranslationDomain, 'plonefrontpage')
            if util is not None:
                translated_text = util.translate(
                    u'front-text',
                    target_language=target_language
                )
                if translated_text != u'front-text':
                    front_text = translated_text
        request = getattr(portal, 'REQUEST', None)
        if front_text is None and request is not None:
            view = queryMultiAdapter(
                (portal, request),
                name='plone-frontpage-setup'
            )
            if view is not None:
                front_text = bodyfinder(view.index()).strip()
        content.text = RichTextValue(
            front_text,
            'text/html',
            'text/x-html-safe'
        )

        portal.setDefaultPage('front-page')
        _publish(content)
        content.reindexObject()


def create_news_topic(portal, target_language):
    news_id = 'news'

    if news_id not in portal.keys():
        title = _translate(u'news-title', target_language, u'News')
        description = _translate(u'news-description', target_language,
                                 u'Site News')
        container = createContent(
            'Folder', id=news_id,
            title=title,
            description=description,
            language=target_language.replace('_', '-').lower())
        container = addContentToContainer(portal, container)
        _createObjectByType('Collection', container,
                            id='aggregator', title=title,
                            description=description)
        aggregator = container['aggregator']

        # Constrain types
        allowed_types = ['News Item', ]
        _setup_constrains(container, allowed_types)

        container.setOrdering('unordered')
        container.setDefaultPage('aggregator')
        _publish(container)

        # Set the Collection criteria.
        #: Sort on the Effective date
        aggregator.sort_on = u'effective'
        aggregator.sort_reversed = True
        #: Query by Type and Review State
        aggregator.query = [
            {'i': u'portal_type',
             'o': u'plone.app.querystring.operation.selection.any',
             'v': [u'News Item'],
             },
            {'i': u'review_state',
             'o': u'plone.app.querystring.operation.selection.any',
             'v': [u'published'],
             },
        ]
        aggregator.setLayout('summary_view')

        _publish(aggregator)


def create_events_topic(portal, target_language):
    events_id = 'events'

    if events_id not in portal.keys():
        title = _translate(u'events-title', target_language, u'Events')
        description = _translate(u'events-description', target_language,
                                 u'Site Events')
        container = createContent(
            'Folder', id=events_id,
            title=title,
            description=description,
            language=target_language.replace('_', '-').lower())
        container = addContentToContainer(portal, container)
        _createObjectByType('Collection', container,
                            id='aggregator', title=title,
                            description=description)
        aggregator = container['aggregator']

        # Constain types
        allowed_types = ['Event', ]

        _setup_constrains(container, allowed_types)

        container.setOrdering('unordered')
        container.setDefaultPage('aggregator')
        _publish(container)

        # Set the Collection criteria.
        #: Sort on the Event start date
        aggregator.sort_on = u'start'
        aggregator.sort_reversed = True
        #: Query by Type and Review State
        aggregator.query = [
            {'i': 'portal_type',
             'o': 'plone.app.querystring.operation.selection.any',
             'v': ['Event']
             },
            {'i': 'review_state',
             'o': 'plone.app.querystring.operation.selection.any',
             'v': ['published']
             },
        ]
        aggregator.setLayout('event_listing')
        _publish(aggregator)


def configure_members_folder(portal, target_language):
    members_id = 'Members'

    if members_id not in portal.keys():
        title = _translate(u'members-title', target_language, u'Users')
        description = _translate(u'members-description', target_language,
                                 u'Site Users')
        container = createContent(
            'Folder', id=members_id,
            title=title,
            description=description,
            language=target_language.replace('_', '-').lower())
        container = addContentToContainer(portal, container)
        container.setOrdering('unordered')
        container.reindexObject()

        # set member search as default layout to Members Area
        container.setLayout('@@member-search')

        # Block all right column portlets by default
        manager = queryUtility(IPortletManager, name='plone.rightcolumn')
        if manager is not None:
            assignable = getMultiAdapter(
                (container, manager),
                ILocalPortletAssignmentManager
            )
            assignable.setBlacklistStatus('context', True)
            assignable.setBlacklistStatus('group', True)
            assignable.setBlacklistStatus('content_type', True)


def import_content(context):
    """Create default content."""
    portal = getSite()
    target_language, is_combined_language, locale = _get_locales_info(portal)
    create_frontpage(portal, target_language)
    create_news_topic(portal, target_language)
    create_events_topic(portal, target_language)
    configure_members_folder(portal, target_language)


def setup_various(context):
    portal = getSite()
    target_language, is_combined_language, locale = _get_locales_info(portal)
    _setup_calendar(portal, locale)
    _setup_visible_ids(portal, target_language, locale)
    use_new_view_names(portal, types_to_fix=['Plone Site'])
