# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from ..utils import replace_link_variables_by_paths


class LinkRedirectView(BrowserView):

    index = ViewPageTemplateFile('templates/link.pt')

    def __call__(self):
        """Redirect to the Link target URL, if and only if:
         - redirect_links property is enabled in
           portal_properties/site_properties
         - AND current user doesn't have permission to edit the Link"""
        context = self.context
        ptool = getToolByName(context, 'portal_properties')
        mtool = getToolByName(context, 'portal_membership')

        redirect_links = getattr(
            ptool.site_properties,
            'redirect_links',
            False
        )
        can_edit = mtool.checkPermission('Modify portal content', context)

        if redirect_links and not can_edit:
            return self.request.RESPONSE.redirect(self.absolute_target_url())
        else:
            return self.index()

    def absolute_target_url(self):
        """Compute the absolute target URL."""
        if self.context.remoteUrl.startswith('.'):
            # we just need to adapt ../relative/links, /absolute/ones work
            # anyway -> this requires relative links to start with ./ or
            # ../
            context_state = self.context.restrictedTraverse(
                '@@plone_context_state'
            )
            url = '/'.join([
                context_state.canonical_object_url(),
                self.context.remoteUrl
            ])
        else:
            url = replace_link_variables_by_paths(
                self.context,
                self.context.remoteUrl
            )
            if not (url.startswith('http://') or url.startswith('https://')):
                url = self.request.physicalPathToURL(url)

        return url
