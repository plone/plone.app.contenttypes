# -*- coding: utf-8 -*-
from plone.app.contenttypes.interfaces import ICollection
from plone.app.contenttypes.interfaces import IDocument
from plone.app.contenttypes.interfaces import IEvent
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IFolder
from plone.app.contenttypes.interfaces import IImage
from plone.app.contenttypes.interfaces import ILink
from plone.app.contenttypes.interfaces import INewsItem
from plone.dexterity.content import Container
from plone.dexterity.content import Item
from zope.interface import implementer


@implementer(ICollection)
class Collection(Item):
    """Convenience subclass for ``Collection`` portal type
    """
    # BBB

    def listMetaDataFields(self, exclude=True):
        """Return a list of all metadata fields from portal_catalog.

        This is no longer used.  We use a vocabulary instead.
        """
        return []

    def selectedViewFields(self):
        """Returns a list of all metadata fields from the catalog that were
           selected.
        """
        from plone.app.contenttypes.behaviors.collection import \
            ICollection as ICollection_behavior
        return ICollection_behavior(self).selectedViewFields()

    def setQuery(self, query):
        self.query = query

    def getQuery(self):
        return self.query

    def setSort_on(self, sort_on):
        self.sort_on = sort_on

    def setSort_reversed(self, sort_reversed):
        self.sort_reversed = sort_reversed

    def queryCatalog(self, batch=True, b_start=0, b_size=30, sort_on=None):
        from plone.app.contenttypes.behaviors.collection import \
            ICollection as ICollection_behavior
        return ICollection_behavior(self).results(
            batch, b_start, b_size, sort_on=sort_on)

    def results(self, **kwargs):
        from plone.app.contenttypes.behaviors.collection import \
            ICollection as ICollection_behavior
        return ICollection_behavior(self).results(**kwargs)


@implementer(IDocument)
class Document(Item):
    """Convenience subclass for ``Document`` portal type
    """


@implementer(IFile)
class File(Item):
    """Convenience subclass for ``File`` portal type
    """


@implementer(IFolder)
class Folder(Container):
    """Convenience subclass for ``Folder`` portal type
    """


@implementer(IImage)
class Image(Item):
    """Convenience subclass for ``Image`` portal type
    """


@implementer(ILink)
class Link(Item):
    """Convenience subclass for ``Link`` portal type
    """


@implementer(INewsItem)
class NewsItem(Item):
    """Convenience subclass for ``News Item`` portal type
    """


@implementer(IEvent)
class Event(Item):
    """Convenience subclass for ``Event`` portal type
    """
