# -*- coding: utf-8 -*-
from zope.interface import Interface, Attribute


class IPloneAppContenttypesLayer(Interface):
    """Marker interface that defines a ZTK browser layer. We can reference
    this in the 'layer' attribute of ZCML <browser:* /> directives to ensure
    the relevant registration only takes effect when this theme is installed.

    The browser layer is installed via the browserlayer.xml GenericSetup
    import step.
    """


class IDocument(Interface):
    """
    """


class IEvent(Interface):
    """
    """
    start_date = Attribute('A start date.')
    end_date = Attribute('An end date.')


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
