# -*- coding: utf-8 -*-
from zope.interface import Interface


class IPloneAppContenttypesLayer(Interface):
    """Marker interface that defines a ZTK browser layer. We can reference
    this in the 'layer' attribute of ZCML <browser:* /> directives to ensure
    the relevant registration only takes effect when this theme is installed.

    The browser layer is installed via the browserlayer.xml GenericSetup
    import step.
    """


class ICollection(Interface):
    """Explixiet marker interface for Collection
    """


class IDocument(Interface):
    """Explixit marker interface for Document
    """


class IFile(Interface):
    """Explixit marker interface for File
    """


class IFolder(Interface):
    """Explixit marker interface for Folder
    """


class IImage(Interface):
    """Explixit marker interface for Image
    """


class ILink(Interface):
    """Explixit marker interface for Link
    """


class INewsItem(Interface):
    """Explixit marker interface for News Item
    """


class IEvent(Interface):
    """Explixit marker interface for Event
    """
