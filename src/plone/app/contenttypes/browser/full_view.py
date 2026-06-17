import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.contenttypes.full_view import FullViewItem instead.",
    FullViewItem="plone.app.layout.contenttypes.full_view:FullViewItem",
)
