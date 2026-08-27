import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.contenttypes.link_redirect_view import "
    "LinkRedirectView, normalize_uid_from_path instead.",
    NON_REDIRECTABLE_URL_SCHEMES="plone.app.layout.contenttypes.link_redirect_view:NON_REDIRECTABLE_URL_SCHEMES",
    NON_RESOLVABLE_URL_SCHEMES="plone.app.layout.contenttypes.link_redirect_view:NON_RESOLVABLE_URL_SCHEMES",
    normalize_uid_from_path="plone.app.layout.contenttypes.link_redirect_view:normalize_uid_from_path",
    LinkRedirectView="plone.app.layout.contenttypes.link_redirect_view:LinkRedirectView",
)
