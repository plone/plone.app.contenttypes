import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.contenttypes.collection import CollectionView instead.",
    CollectionView="plone.app.layout.contenttypes.collection:CollectionView",
)
