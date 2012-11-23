# -*- coding: utf-8 -*-
from zope.interface import Interface, Attribute


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
