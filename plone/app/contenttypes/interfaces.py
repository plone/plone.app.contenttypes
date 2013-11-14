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
    """
    """


class IDocument(Interface):
    """
    """


class IFile(Interface):
    """
    """


class IFolder(Interface):
    """
    """


class IImage(Interface):
    """
    """


class ILink(Interface):
    """
    """


class INewsItem(Interface):
    """
    """


class IEvent(Interface):
    """
    """
