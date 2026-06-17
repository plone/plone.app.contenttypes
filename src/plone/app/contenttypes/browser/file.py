import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.contenttypes.file import FileView instead.",
    FileView="plone.app.layout.contenttypes.file:FileView",
)
