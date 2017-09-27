# -*- coding: utf-8 -*-
from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
from zope.component import getUtility
from zope.publisher.interfaces.browser import IBrowserView


class FullViewItem(BrowserView):

    @property
    def default_view(self):
        item_layout = self.context.getLayout()
        default_view = self.context.restrictedTraverse(item_layout)
        return default_view

    @property
    def item_macros(self):
        default_view = self.default_view
        if IBrowserView.providedBy(default_view):
            # IBrowserView
            return default_view.index.macros
        # FSPageTemplate
        return default_view.macros

    @property
    def item_url(self):
        registry = getUtility(IRegistry)
        use_view_action = registry.get(
            'plone.types_use_view_action_in_listings', [])
        url = self.context.absolute_url()
        if self.context.portal_type in use_view_action:
            url = u'{0}/view'.format(url)
        return url
