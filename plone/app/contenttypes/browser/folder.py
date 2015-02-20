# -*- coding: utf-8 -*-
from Acquisition import aq_base
from Products.CMFPlone.PloneBatch import Batch
from Products.CMFPlone.utils import safe_callable
from Products.Five import BrowserView
from plone.app.contenttypes import _
from plone.event.interfaces import IEvent
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.contentprovider.interfaces import IContentProvider

HAS_SECURITY_SETTINGS = True
try:
    from Products.CMFPlone.interfaces import ISecuritySchema
except ImportError:
    HAS_SECURITY_SETTINGS = False


class FolderView(BrowserView):

    def __init__(self, context, request):
        super(FolderView, self).__init__(context, request)

        registry = getUtility(IRegistry)

        self.plone_view = getMultiAdapter(
            (context, request), name=u"plone")

        self.portal_state = getMultiAdapter(
            (context, request), name=u"plone_portal_state")
        self.friendly_types = self.portal_state.friendly_types()
        self.isAnon = self.portal_state.anonymous()
        self.navigation_root_url = self.portal_state.navigation_root_url()

        # BBB
        self.site_properties = context.restrictedTraverse(
            'portal_properties').site_properties
        self.use_view_action = getattr(
            self.site_properties, 'typesUseViewActionInListings', ())

        if HAS_SECURITY_SETTINGS:
            security_settings = registry.forInterface(
                ISecuritySchema, prefix="plone")
            self.show_about = getattr(
                security_settings, 'allow_anon_views_about', False
            ) or not self.isAnon
        else:
            # BBB
            self.show_about = getattr(
                self.site_properties, 'allowAnonymousViewAbout', False
            ) or not self.isAnon

        self.pas_member = getMultiAdapter(
            (context, request), name=u"pas_member")

        self.text_class = None

        limit_display = getattr(self.request, 'limit_display', None)
        limit_display = int(limit_display) if limit_display is not None else 20
        b_size = getattr(self.request, 'b_size', None)
        self.b_size = int(b_size) if b_size is not None else limit_display
        b_start = getattr(self.request, 'b_start', None)
        self.b_start = int(b_start) if b_start is not None else 0

    def _content_filter(self):
        content_filter = getattr(self.request, 'contentFilter', None)
        content_filter = dict(content_filter) if content_filter else {}
        content_filter.setdefault('portal_type', self.friendly_types)
        content_filter.setdefault('batch', True)
        content_filter.setdefault('b_size', self.b_size)
        content_filter.setdefault('b_start', self.b_start)
        return content_filter

    def results(self):
        results = self.context.restrictedTraverse(
            '@@folderListing')(**self._content_filter())
        return results

    def batch(self):
        batch = Batch(self.results(), self.b_size, self.b_start, orphan=1)
        return batch

    def normalizeString(self, text):
        return self.plone_view.normalizeString(text)

    def toLocalizedTime(self, time, long_format=None, time_only=None):
        return self.plone_view.toLocalizedTime(time, long_format, time_only)

    def text(self):
        textfield = getattr(aq_base(self.context), 'text', None)
        text = getattr(textfield, 'output', None)
        if text:
            self.text_class = 'stx' if textfield.mimeType in (
                'text/structured', 'text/x-rst', 'text/restructured'
            ) else 'plain'
        return text

    def tabular_fields(self):
        ret = []
        ret.append('Title')
        if self.show_about:
            ret.append('Creator')
        ret.append('Type')
        if self.show_about:
            ret.append('ModificationDate')
        return ret

    def tabular_fielddata(self, item, fieldname):
        value = getattr(item, fieldname, '')
        if safe_callable(value):
            value = value()
        if fieldname in [
                'CreationDate',
                'ModificationDate',
                'Date',
                'EffectiveDate',
                'ExpirationDate',
                'effective',
                'expires',
                'start',
                'end',
                'created',
                'modified',
                'last_comment_date']:
            value = self.toLocalizedTime(value, long_format=1)

        return {
            # 'title': _(fieldname, default=fieldname),
            'value': value
        }

    def is_event(self, obj):
        return IEvent.providedBy(obj)

    def formatted_date(self, item):
        provider = getMultiAdapter(
            (self.context, self.request, self),
            IContentProvider, name='formatted_date'
        )
        return provider(item)

    def no_items_message(self):
        return _(
            'description_no_items_in_folder',
            default=u"There are currently no items in this folder."
        )
