from zope.interface import alsoProvides
from plone.dexterity.interfaces import IDexterityContent
from Products.Five.browser import BrowserView

from Products.CMFCore.utils import getToolByName
from plone.app.contenttypes.interfaces import (
    IDocument,
    IEvent,
    IFile,
    IFolder,
    IImage,
    ILink,
    INewsItem,
)


class FixInterfaces(BrowserView):

    def __call__(self):
        """Make sure all content objects implement the proper interfaces.
        """
        out = ""
        catalog = getToolByName(self.context, "portal_catalog")
        portal_types = [
            ('Document', IDocument),
            ('Event', IEvent),
            ('File', IFile),
            ('Folder', IFolder),
            ('Image', IImage),
            ('Link', ILink),
            ('News Item', INewsItem),
        ]
        for portal_type, portal_type_interface in portal_types:
            results = catalog.searchResults(portal_type=portal_type)
            for brain in results:
                obj = brain.getObject()
                if IDexterityContent.providedBy(obj):
                    if not portal_type_interface.providedBy(obj):
                        alsoProvides(obj, portal_type_interface)
                        out += "Make %s provide %s\n" % (
                            obj.Title(),
                            portal_type_interface.__name__,
                        )
        return out
