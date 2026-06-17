import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.contenttypes.utils import IUtils, Utils instead.",
    PREFIX="plone.app.layout.contenttypes.utils:PREFIX",
    IUtils="plone.app.layout.contenttypes.utils:IUtils",
    Utils="plone.app.layout.contenttypes.utils:Utils",
)
