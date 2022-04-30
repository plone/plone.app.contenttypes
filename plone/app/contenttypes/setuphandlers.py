from AccessControl import Unauthorized
from Acquisition import aq_base
from Acquisition import aq_inner
from plone.app.dexterity.behaviors import constrains
from plone.app.textfield.value import RichTextValue
from plone.base.interfaces import INonInstallable
from plone.base.interfaces.constrains import ISelectableConstrainTypes
from plone.base.utils import unrestricted_construct_instance
from plone.dexterity.fti import IDexterityFTI
from plone.dexterity.utils import createContent
from plone.i18n.normalizer.interfaces import IURLNormalizer
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletManager
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
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
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        """
        Prevents all profiles but 'plone-content' from showing up in the
        profile list when creating a Plone site.
        """
        return [
            "plone.app.contenttypes:default",
        ]


def _publish(content):
    """Publish the object if it hasn't been published."""
    portal_workflow = getToolByName(getSite(), "portal_workflow")
    if portal_workflow.getInfoFor(content, "review_state") != "published":
        portal_workflow.doActionFor(content, "publish")
        return True
    return False


def _translate(name, target_language, default=""):
    """Simple function to translate a string."""
    result = None
    if target_language != "en":
        util = queryUtility(ITranslationDomain, "plonefrontpage")
        if util is not None:
            result = util.translate(
                name, target_language=target_language, default=default
            )
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
            raise Unauthorized(f"Cannot create {object.portal_type}")

        if container_fti is not None and not container_fti.allowType(
            object.portal_type
        ):
            raise ValueError(f"Disallowed subobject type: {object.portal_type}")

    chooser = INameChooser(container)
    if hasattr(object, "id") and chooser.checkName(object.id, object):
        name = object.id
    else:
        name = INameChooser(container).chooseName(None, object)
        object.id = name

    newName = container._setObject(name, object)
    return container._getOb(newName)


def _get_locales_info(portal):
    reg = queryUtility(IRegistry, context=portal)
    language = reg["plone.default_language"]
    parts = (language.split("-") + [None, None])[:3]

    try:
        locale = locales.getLocale(*parts)

        # If we get a territory, we enable the combined language codes
        if locale.id.territory:
            return locale.id.language + "_" + locale.id.territory, True, locale
        return locale.id.language, False, locale
    except LoadLocaleError:
        # default to *some* language so we don't error out
        return language, False, locales.getLocale("en")


def _setup_calendar(portal, locale):
    """Set the calendar's date system to reflect the default locale"""
    gregorian_calendar = locale.dates.calendars.get("gregorian", None)
    portal_calendar = getToolByName(portal, "portal_calendar", None)
    if portal_calendar is not None:
        first = 6
        if gregorian_calendar is not None:
            first = gregorian_calendar.week.get("firstDay", None)
            # on the locale object we have: mon : 1 ... sun : 7
            # on the calendar tool we have: mon : 0 ... sun : 6
            if first is not None:
                first = first - 1
        portal_calendar.firstweekday = first


def _setup_visible_ids(portal, target_language, locale):
    portal_properties = getToolByName(portal, "portal_properties")
    site_properties = portal_properties.site_properties

    # See if we have a URL normalizer
    normalizer = queryUtility(IURLNormalizer, name=target_language)
    if normalizer is None:
        normalizer = queryUtility(IURLNormalizer)

    # If we get a script other than Latn we enable visible_ids
    if locale.id.script is not None:
        if locale.id.script.lower() != "latn":
            site_properties.visible_ids = True

    # If we have a normalizer it is safe to disable the visible ids
    if normalizer is not None:
        site_properties.visible_ids = False


def _setup_constrains(container, allowed_types):
    behavior = ISelectableConstrainTypes(container)
    behavior.setConstrainTypesMode(constrains.ENABLED)
    behavior.setImmediatelyAddableTypes(allowed_types)
    return True


def _bodyfinder(text):
    """Return body or unchanged text if no body tags found.

    Always use html_headcheck() first.
    """
    lowertext = text.lower()
    bodystart = lowertext.find("<body")
    if bodystart == -1:
        return text
    bodystart = lowertext.find(">", bodystart) + 1
    if bodystart == 0:
        return text
    bodyend = lowertext.rfind("</body>", bodystart)
    if bodyend == -1:
        return text
    return text[bodystart:bodyend]


def create_frontpage(portal, target_language):
    if portal.text:
        # Do not overwrite existing content
        return
    portal.title = _translate("front-title", target_language, "Welcome to Plone")
    portal.description = _translate(
        "front-description",
        target_language,
        "Congratulations! You have successfully installed Plone.",
    )
    front_text = None
    if target_language != "en":
        util = queryUtility(ITranslationDomain, "plonefrontpage")
        if util is not None:
            translated_text = util.translate(
                "front-text", target_language=target_language
            )
            if translated_text != "front-text":
                front_text = translated_text
    request = getattr(portal, "REQUEST", None)
    if front_text is None and request is not None:
        view = queryMultiAdapter((portal, request), name="plone-frontpage-setup")
        if view is not None:
            front_text = _bodyfinder(view.index()).strip()
    portal.text = RichTextValue(front_text, "text/html", "text/x-html-safe")
    portal.reindexObject()


def create_news_topic(portal, target_language):
    news_id = "news"

    if news_id not in portal.keys():
        title = _translate("news-title", target_language, "News")
        description = _translate("news-description", target_language, "Site News")
        container = createContent(
            "Folder",
            id=news_id,
            title=title,
            description=description,
            language=target_language.replace("_", "-").lower(),
        )
        container = addContentToContainer(portal, container)
        unrestricted_construct_instance(
            "Collection",
            container,
            id="aggregator",
            title=title,
            description=description,
        )
        aggregator = container["aggregator"]

        # Constrain types
        allowed_types = [
            "News Item",
        ]
        _setup_constrains(container, allowed_types)

        container.setOrdering("unordered")
        container.setDefaultPage("aggregator")
        _publish(container)

        # Set the Collection criteria.
        #: Sort on the Effective date
        aggregator.sort_on = "effective"
        aggregator.sort_reversed = True
        #: Query by Type and Review State
        aggregator.query = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.selection.any",
                "v": ["News Item"],
            },
            {
                "i": "review_state",
                "o": "plone.app.querystring.operation.selection.any",
                "v": ["published"],
            },
        ]
        aggregator.setLayout("summary_view")

        _publish(aggregator)


def create_events_topic(portal, target_language):
    events_id = "events"

    if events_id not in portal.keys():
        title = _translate("events-title", target_language, "Events")
        description = _translate("events-description", target_language, "Site Events")
        container = createContent(
            "Folder",
            id=events_id,
            title=title,
            description=description,
            language=target_language.replace("_", "-").lower(),
        )
        container = addContentToContainer(portal, container)
        unrestricted_construct_instance(
            "Collection",
            container,
            id="aggregator",
            title=title,
            description=description,
        )
        aggregator = container["aggregator"]

        # Constain types
        allowed_types = [
            "Event",
        ]

        _setup_constrains(container, allowed_types)

        container.setOrdering("unordered")
        container.setDefaultPage("aggregator")
        _publish(container)

        # Set the Collection criteria.
        #: Sort on the Event start date
        aggregator.sort_on = "start"
        aggregator.sort_reversed = True
        #: Query by Type and Review State
        aggregator.query = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.selection.any",
                "v": ["Event"],
            },
            {
                "i": "review_state",
                "o": "plone.app.querystring.operation.selection.any",
                "v": ["published"],
            },
        ]
        aggregator.setLayout("event_listing")
        _publish(aggregator)


def configure_members_folder(portal, target_language):
    members_id = "Members"

    if members_id not in portal.keys():
        title = _translate("members-title", target_language, "Users")
        description = _translate("members-description", target_language, "Site Users")
        container = createContent(
            "Folder",
            id=members_id,
            title=title,
            description=description,
            language=target_language.replace("_", "-").lower(),
        )
        container = addContentToContainer(portal, container)
        container.setOrdering("unordered")
        container.reindexObject()

        # set member search as default layout to Members Area
        container.setLayout("@@member-search")

        # Block all right column portlets by default
        manager = queryUtility(IPortletManager, name="plone.rightcolumn")
        if manager is not None:
            assignable = getMultiAdapter(
                (container, manager), ILocalPortletAssignmentManager
            )
            assignable.setBlacklistStatus("context", True)
            assignable.setBlacklistStatus("group", True)
            assignable.setBlacklistStatus("content_type", True)


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
