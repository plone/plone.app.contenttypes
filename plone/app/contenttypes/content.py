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
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from zope.deprecation import deprecation
from zope.interface import implementer
from zope.lifecycleevent import modified


import six


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
        """Return the query as a list of dict; note that this method
        returns a list of CatalogContentListingObject in
        Products.ATContentTypes.
        """
        return self.query

    @deprecation.deprecate('getRawQuery() is deprecated; use getQuery().')
    def getRawQuery(self):
        return self.getQuery()

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

    def PUT(self, REQUEST=None, RESPONSE=None):
        """DAV method to replace the file field with a new resource."""
        request = REQUEST if REQUEST is not None else self.REQUEST
        response = RESPONSE if RESPONSE is not None else request.response

        self.dav__init(request, response)
        self.dav__simpleifhandler(request, response, refresh=1)

        infile = request.get('BODYFILE', None)
        filename = request['PATH_INFO'].split('/')[-1]
        self.file = NamedBlobFile(
            data=infile.read(), filename=six.text_type(filename))

        modified(self)
        return response

    def get_size(self):
        return getattr(self.file, 'size', 0)

    def content_type(self):
        return getattr(self.file, 'contentType', None)


@implementer(IFolder)
class Folder(Container):
    """Convenience subclass for ``Folder`` portal type
    """


@implementer(IImage)
class Image(Item):
    """Convenience subclass for ``Image`` portal type
    """

    def PUT(self, REQUEST=None, RESPONSE=None):
        """DAV method to replace image field with a new resource."""
        request = REQUEST if REQUEST is not None else self.REQUEST
        response = RESPONSE if RESPONSE is not None else request.response

        self.dav__init(request, response)
        self.dav__simpleifhandler(request, response, refresh=1)

        infile = request.get('BODYFILE', None)
        filename = request['PATH_INFO'].split('/')[-1]
        self.image = NamedBlobImage(
            data=infile.read(), filename=six.text_type(filename))

        modified(self)
        return response

    def get_size(self):
        return getattr(self.image, 'size', 0)

    def content_type(self):
        return getattr(self.image, 'contentType', None)


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
