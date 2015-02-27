from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
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
        props = getToolByName(context, 'portal_properties')
        use_view_action = props.site_properties.typesUseViewActionInListings
        return self.item_type in use_view_action and '%s/view' % url or url
