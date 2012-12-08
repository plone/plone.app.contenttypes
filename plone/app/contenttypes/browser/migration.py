from plone.dexterity.interfaces import IDexterityContent
from Products.Five.browser import BrowserView

from Products.CMFCore.utils import getToolByName
from plone.app.contenttypes.content import (
    Document,
    Event,
    File,
    Folder,
    Image,
    Link,
    NewsItem,
)


class FixInterfaces(BrowserView):

    def __call__(self):
        """Make sure all content objects implement the proper interfaces.
        """
        out = ""
        catalog = getToolByName(self.context, "portal_catalog")
        portal_types = [
            ('Document', Document),
            ('Event', Event),
            ('File', File),
            ('Folder', Folder),
            ('Image', Image),
            ('Link', Link),
            ('News Item', NewsItem),
        ]
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
