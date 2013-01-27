from plone.dexterity.interfaces import IDexterityContent

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView


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
        out = '\n'.join([migration.migrate_documents(portal),
                         migration.migrate_files(portal),
                         migration.migrate_images(portal),
                         migration.migrate_newsitems(portal),
                         migration.migrate_links(portal),
                         migration.migrate_folders(portal)])
        return out
