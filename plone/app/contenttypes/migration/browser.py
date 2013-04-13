# -*- coding: utf-8 -*-
from pprint import pformat
from zope.interface import Interface
from zope import schema
from z3c.form import form, button, field
from z3c.form.browser.checkbox import CheckBoxFieldWidget

from plone.z3cform.layout import wrap_form

from plone.dexterity.interfaces import IDexterityContent

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# Old interfaces
from Products.ATContentTypes.interfaces.document import IATDocument
from Products.ATContentTypes.interfaces.file import IATFile
from Products.ATContentTypes.interfaces.folder import IATFolder
from Products.ATContentTypes.interfaces.image import IATImage
from Products.ATContentTypes.interfaces.link import IATLink
from Products.ATContentTypes.interfaces.news import IATNewsItem
# from Products.Archetypes.interfaces import IBaseObject


try:
    from plone.app.collection.interfaces import ICollection
    HAS_APP_COLLECTION = True
except ImportError:
    ICollection = None
    HAS_APP_COLLECTION = False


# Schema Extender allowed interfaces
from archetypes.schemaextender.interfaces import (
    ISchemaExtender,
    IOrderableSchemaExtender,
    IBrowserLayerAwareExtender,
    ISchemaModifier
)

# This is required for finding schema extensions
from zope.component import getGlobalSiteManager

from plone.app.contenttypes.content import (
    Document,
    Event,
    File,
    Folder,
    Image,
    Link,
    NewsItem,
)

from . import migration


class FixBaseClasses(BrowserView):

    def __call__(self):
        """Make sure all content objects use the proper base classes.
           Instances before version 1.0b1 had no base-class.
           To update them call @@fix_base_classes on your site-root.
        """
        out = ""
        portal_types = [
            ('Document', Document),
            ('Event', Event),
            ('File', File),
            ('Folder', Folder),
            ('Image', Image),
            ('Link', Link),
            ('News Item', NewsItem),
        ]
        catalog = getToolByName(self.context, "portal_catalog")
        for portal_type, portal_type_class in portal_types:
            results = catalog.searchResults(portal_type=portal_type)
            for brain in results:
                obj = brain.getObject()
                if IDexterityContent.providedBy(obj):
                    object_class_name = obj.__class__.__name__
                    target_class_name = portal_type_class.__name__
                    if not object_class_name == target_class_name:
                        obj.__class__ = portal_type_class
                        out += "Make %s use %s\n as base class." % (
                            obj.Title(),
                            portal_type_class.__name__,
                        )
        return out


class MigrateFromATContentTypes(BrowserView):
    """ Migrate the default-types (except event and topic)
    """

    def __call__(self):
        stats_before = 'State before:\n'
        stats_before += self.stats()
        portal = self.context

        # Check whether and of the default content types have had their
        # schemas extended
        not_migrated = []
        if not self._isSchemaExtended(IATFolder):
            migration.migrate_folders(portal)
        else:
            not_migrated.append("Folder")
        if not self._isSchemaExtended(IATDocument):
            migration.migrate_documents(portal)
        else:
            not_migrated.append("Document")
        if not self._isSchemaExtended(IATFile):
            migration.migrate_files(portal)
        else:
            not_migrated.append("File")
        if not self._isSchemaExtended(IATImage):
            migration.migrate_images(portal)
        else:
            not_migrated.append("Image")
        if not self._isSchemaExtended(IATNewsItem):
            migration.migrate_newsitems(portal)
        else:
            not_migrated.append("NewsItem")
        if not self._isSchemaExtended(IATLink):
            migration.migrate_links(portal)
        else:
            not_migrated.append("Link")
        if HAS_APP_COLLECTION and not self._isSchemaExtended(ICollection):
            migration.migrate_collections(portal)
        else:
            not_migrated.append("Collection")

        # blobfiles and images are always schma-extended
        # we need to find out if they are extended even further
        # in another way
        migration.migrate_blobimages(portal)
        migration.migrate_blobfiles(portal)
        migration.migrate_blobnewsitems(portal)

        migration.restoreReferences(portal)
        migration.restoreReferencesOrder(portal)

        if not_migrated:
            msg = ("The following cannot be migrated as they "
                   "have extended schemas (from "
                   "archetypes.schemaextender): \n %s"
                   % "\n".join(not_migrated))
        else:
            msg = "Default content types successfully migrated\n\n"

        msg += '\n-----------------------------\n'
        msg += stats_before
        msg += '\n-----------------------------\n'
        msg += 'Stats after:\n'
        msg += self.stats()
        msg += '\n-----------------------------\n'
        msg += 'migration done - somehow. Be careful!'
        return msg

    def _isSchemaExtended(self, interface):
        sm = getGlobalSiteManager()
        extender_interfaces = [
            ISchemaExtender,
            ISchemaModifier,
            IBrowserLayerAwareExtender,
            IOrderableSchemaExtender]
        # We have a few possible interfaces to test
        # here, so get all the interfaces that
        # are for the given content type first
        registrations = \
            [a for a in sm.registeredAdapters() if interface in a.required]
        for adapter in registrations:
            if adapter.provided in extender_interfaces:
                return True
        return False

    def stats(self):
        results = {}
        for brain in self.context.portal_catalog():
            classname = brain.getObject().__class__.__name__
            results[classname] = results.get(classname, 0) + 1
        return pformat(sorted(results.items()))


class IATCTMigrationForm(Interface):

    content_types = schema.List(
        title=u"Content types to migrate",
        description=u"Select which content types you want to migrate",
        value_type=schema.Choice(
            vocabulary="plone.app.contenttypes.migration.atcttypes",
        )
    )

    migrate_references = schema.Bool(
        title=u"Migrate references?",
        description=(
            u"Select this option to migrate all "
            u"references to each content type"
        ),
        default=True
    )

    migrate_schemaextended_content = schema.Bool(
        title=(
            u"Migrate content that was extended "
            u"trough archetypes.schemaextender?"
        ),
        description=(
            u"Please, pay attention. You will lose the data "
            u"in the in the extended Fields"
        ),
        default=False
    )


class ATCTMigrationForm(form.Form):

    fields = field.Fields(IATCTMigrationForm)
    fields['content_types'].widgetFactory = CheckBoxFieldWidget
    ignoreContext = True

    @button.buttonAndHandler(u'Migrate', name='migrate')
    def handle_migrate(self, action):
        data, errors = self.extractData()

    def updateActions(self):
        super(ATCTMigrationForm, self).updateActions()
        self.actions['migrate'].addClass("btn-danger")


ATCTMigration = wrap_form(
    ATCTMigrationForm,
    index=ViewPageTemplateFile('atct_migration.pt')
)
