# -*- coding: utf-8 -*-
import pkg_resources
from zope.component import getGlobalSiteManager

from Products.ATContentTypes.interfaces.document import IATDocument
from Products.ATContentTypes.interfaces.file import IATFile
from Products.ATContentTypes.interfaces.folder import IATFolder
from Products.ATContentTypes.interfaces.image import IATImage
from Products.ATContentTypes.interfaces.link import IATLink
from Products.ATContentTypes.interfaces.news import IATNewsItem

# Schema Extender allowed interfaces
from archetypes.schemaextender.interfaces import (
    ISchemaExtender,
    IOrderableSchemaExtender,
    IBrowserLayerAwareExtender,
    ISchemaModifier
)

try:
    pkg_resources.get_distribution('plone.app.collection')
except pkg_resources.DistributionNotFound:
    ICollection = None
    HAS_APP_COLLECTION = False
else:
    HAS_APP_COLLECTION = True
    from plone.app.collection.interfaces import ICollection


CT_LIST = (
    ("Folder", IATFolder),
    ("Document", IATDocument),
    ("File", IATFile),
    ("Image", IATImage),
    ("News Item", IATNewsItem),
    ("Link", IATLink)
)

if HAS_APP_COLLECTION:
    CT_LIST += (("Collection", ICollection), )


def isSchemaExtended(interface):
    """Return whether a specific content type interface
    is extended by archetypes.schemaextender or not
    """
    sm = getGlobalSiteManager()
    extender_interfaces = [
        ISchemaExtender,
        ISchemaModifier,
        IBrowserLayerAwareExtender,
        IOrderableSchemaExtender]
    # We have a few possible interfaces to test
    # here, so get all the interfaces that
    # are for the given content type first
    registrations = \
        [a for a in sm.registeredAdapters() if interface in a.required]
    for adapter in registrations:
        if adapter.provided in extender_interfaces:
            return True
    return False
