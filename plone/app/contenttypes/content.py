# -*- coding: utf-8 -*-
from plone.app.contenttypes.interfaces import (
    ICollection,
    IDocument,
    IFile,
    IFolder,
    IImage,
    ILink,
    INewsItem,
    IEvent,
)

from plone.dexterity.content import Item
from plone.dexterity.content import Container

from zope.interface import implements


class Collection(Item):
    implements(ICollection)

    #security.declareProtected(View, 'listMetaDataFields')
    def listMetaDataFields(self, exclude=True):
        """Return a list of all metadata fields from portal_catalog.
        """
        return []
        #tool = getToolByName(self, ATCT_TOOLNAME)
        #return tool.getMetadataDisplay(exclude)

    def selectedViewFields(self):
        """Returns a list of all metadata fields from the catalog that were
           selected.
        """
        return []
        #_mapping = {}
        #for field in self.listMetaDataFields().items():
        #    _mapping[field[0]] = field
        #return [_mapping[field] for field in self.customViewFields]

    # BBB

    def setQuery(self, query):
        self.query = query

    def getQuery(self):
        return self.query

    def setSort_on(self, sort_on):
        self.sort_on = sort_on

    def setSort_reversed(self, sort_reversed):
        self.sort_reversed = sort_reversed

    def queryCatalog(self, batch=True, b_start=0, b_size=30, sort_on=None):
        return self.results(
            batch, b_start, b_size, sort_on=sort_on
        )


class Document(Item):
    implements(IDocument)


class File(Item):
    implements(IFile)


class Folder(Container):
    implements(IFolder)


class Image(Item):
    implements(IImage)


class Link(Item):
    implements(ILink)


class NewsItem(Item):
    implements(INewsItem)


class Event(Item):
    implements(IEvent)
