# -*- coding: utf-8 -*-
from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import ITypesSchema
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.contenttypes.utils import replace_link_variables_by_paths
from plone.registry.interfaces import IRegistry


# links starting with these URL scheme should not be redirected to
NON_REDIRECTABLE_URL_SCHEMES = [
    'mailto:',
    'tel:',
    'callto:',
    'webdav:',
    'caldav:'
]

# links starting with these URL scheme should not be resolved to paths
NON_RESOLVABLE_URL_SCHEMES = NON_REDIRECTABLE_URL_SCHEMES + [
    'file:',
    'ftp:',
]


class LinkRedirectView(BrowserView):

    index = ViewPageTemplateFile('templates/link.pt')

    def _url_uses_scheme(self, schemes, url=None):
        url = url or self.context.remoteUrl
        for scheme in schemes:
            if url.startswith(scheme):
                return True
        return False

    def __call__(self):
        """Redirect to the Link target URL, if and only if:
         - redirect_links property is enabled in
           configuration registry
         - the link is of a redirectable type (no mailto:, etc)
         - AND current user doesn't have permission to edit the Link"""
        context = self.context
        mtool = getToolByName(context, 'portal_membership')

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ITypesSchema, prefix="plone")
        redirect_links = settings.redirect_links

        can_edit = mtool.checkPermission('Modify portal content', context)
        redirect_links = redirect_links\
            and not self._url_uses_scheme(NON_REDIRECTABLE_URL_SCHEMES)

        if redirect_links and not can_edit:
            return self.request.RESPONSE.redirect(self.absolute_target_url())
        else:
            return self.index()

    def absolute_target_url(self):
        """Compute the absolute target URL."""
        url = self.context.remoteUrl

        if self._url_uses_scheme(NON_RESOLVABLE_URL_SCHEMES):
            # For non http/https url schemes, there is no path to resolve.
            return url

        if url.startswith('.'):
            # we just need to adapt ../relative/links, /absolute/ones work
            # anyway -> this requires relative links to start with ./ or
            # ../
            context_state = self.context.restrictedTraverse(
                '@@plone_context_state'
            )
            url = '/'.join([
                context_state.canonical_object_url(),
                url
            ])
        else:
            url = replace_link_variables_by_paths(self.context, url)
            if not (url.startswith('http://') or url.startswith('https://')):
                url = self.request.physicalPathToURL(url)

        return url
