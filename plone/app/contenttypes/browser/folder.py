# -*- coding: utf-8 -*-
from Acquisition import aq_base
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from Products.CMFPlone.PloneBatch import Batch


class FolderView(BrowserView):

    def __init__(self, context, request):
        super(FolderView, self).__init__(context, request)

        self.plone_view = getMultiAdapter(
            (context, request), name=u"plone")

        self.portal_state = getMultiAdapter(
            (context, request), name=u"plone_portal_state")
        self.friendly_types = self.portal_state.friendly_types()
        self.isAnon = self.portal_state.anonymous()
        self.navigation_root_url = self.portal_state.navigation_root_url()

        self.site_properties = context.restrictedTraverse(
            'portal_properties').site_properties
        self.use_view_action = getattr(
            self.site_properties, 'typesUseViewActionInListings', ())
        self.show_about = getattr(
            self.site_properties, 'allowAnonymousViewAbout', not self.isAnon)

        # TODO: REMOVE
        self.more_url = getattr(request, 'more_url', 'folder_contents')

        # TODO: eventually REMOVE
        self.plone_layout = context.restrictedTraverse('@@plone_layout')

        self.pas_member = context.restrictedTraverse('@@pas_member')

        limit_display = getattr(request, 'limit_display', None)
        limit_display = int(limit_display) if limit_display is not None else 20
        b_size = getattr(request, 'b_size', None)
        b_size = int(b_size) if b_size is not None else limit_display
        b_start = getattr(request, 'b_start', None)
        b_start = int(b_start) if b_start is not None else 0

        contentFilter = getattr(request, 'contentFilter', None)
        contentFilter = dict(contentFilter) if contentFilter else {}
        contentFilter.setdefault('portal_type', self.friendly_types)
        contentFilter.setdefault('batch', True)
        contentFilter.setdefault('b_size', b_size)
        contentFilter.setdefault('b_start', b_start)

        self.folderContents = context.restrictedTraverse(
            '@@folderListing')(**contentFilter)

        self.batch = Batch(self.folderContents, b_size, b_start, orphan=1)

        self.text_class = None

    def normalizeString(self, text):
        return self.plone_view.normalizeString(text)

    def toLocalizedTime(self, time, long_format=None, time_only=None):
        return self.plone_view.toLocalizedTime(time, long_format, time_only)

    def text(self):
        textfield = getattr(aq_base(self.context), 'text', None)
        text = getattr(textfield, 'output', None)
        if text:
            self.text_class = 'stx' if textfield.contentType() in (
                'text/structured', 'text/x-rst', 'text/restructured'
            ) else 'plain'
        return text
