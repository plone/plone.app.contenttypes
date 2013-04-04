# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName


class LinkRedirectView(BrowserView):

    template = ViewPageTemplateFile('templates/link.pt')

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
            if context.remoteUrl.startswith('.'):
                # we just need to adapt ../relative/links, /absolute/ones work
                # anyway -> this requires relative links to start with ./ or
                # ../
                context_state = context.restrictedTraverse(
                    '@@plone_context_state'
                )
                return context.REQUEST.RESPONSE.redirect(
                    context_state.canonical_object_url() +
                    '/' +
                    context.remoteUrl
                )
            else:
                portal_state = context.restrictedTraverse(
                    "@@plone_portal_state"
                )
                if "${navigation_root_url}" in context.remoteUrl:
                    navigation_root_url = portal_state.navigation_root_url()
                    url = context.remoteUrl.replace(
                        "${navigation_root_url}",
                        navigation_root_url
                    )
                elif "${portal_url}" in context.remoteUrl:
                    portal_url = portal_state.portal_url()
                    url = context.remoteUrl.replace(
                        "${portal_url}",
                        portal_url
                    )
                else:
                    url = context.remoteUrl
                return context.REQUEST.RESPONSE.redirect(url)
        else:
            return self.template()
