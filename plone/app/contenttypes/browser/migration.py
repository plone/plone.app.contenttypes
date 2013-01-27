from plone.dexterity.interfaces import IDexterityContent

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

# Old interfaces
from Products.ATContentTypes.interfaces.document import IATDocument
from Products.ATContentTypes.interfaces.file import IATFile
from Products.ATContentTypes.interfaces.image import IATImage
from Products.ATContentTypes.interfaces.link import IATLink
from Products.ATContentTypes.interfaces.news import IATNewsItem

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
try:
    from plone.app.contenttypes import migration
    HAS_ATCT_MIGRATION = True
except ImportError:
    HAS_ATCT_MIGRATION = False


class FixBaseClasses(BrowserView):

    def __call__(self):
        """Make sure all content objects use the proper base classes.
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

    def __call__(self):

        if not HAS_ATCT_MIGRATION:
            msg = ('You want to migrate ATContentType object to '
                   'plone.app.contetntypes objects, but we can not '
                   'find Products.contentmigration. '
                   'You can fix that by installing plone.app.contenttypes '
                   'with the extra_requires [migrate_atct]')
            return msg
        portal = self.context
        
        # Check whether and of the default content types have had their
        # schemas extended
        not_migrated = []
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
            
        migration.restoreReferences(portal)
        
        if not_migrated:
            msg = ("The following cannot be migrated as they "
                   "have extended schemas (from "
                   "archetypes.schemaextender): \n %s" 
                   % "\n".join(not_migrated))
        else:
            msg = "Default content types successfully migrated"
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
