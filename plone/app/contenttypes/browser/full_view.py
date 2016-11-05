# -*- coding: utf-8 -*-
from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
from zope.component import getUtility
from zope.publisher.interfaces.browser import IBrowserView


class FullViewItem(BrowserView):

    def __init__(self, context, request):
        super(FullViewItem, self).__init__(context, request)
        self.item_type = self.context.portal_type

    @property
    def default_view(self):
        context = self.context
        item_layout = context.getLayout()
        default_view = context.restrictedTraverse(item_layout)
        return default_view

    @property
    def item_macros(self):
        default_view = self.default_view
        if IBrowserView.providedBy(default_view):
            # IBrowserView
            return default_view.index.macros
        else:
            # FSPageTemplate
            return default_view.macros

    @property
    def item_url(self):
        context = self.context
        url = context.absolute_url()
        registry = getUtility(IRegistry)
        use_view_action = registry.get(
            'plone.types_use_view_action_in_listings', [])
        view_url = '{0}/view'.format(url)
        return self.item_type in use_view_action and view_url or url
