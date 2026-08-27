import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.contenttypes.folder import FolderView instead.",
    FolderView="plone.app.layout.contenttypes.folder:FolderView",
)
