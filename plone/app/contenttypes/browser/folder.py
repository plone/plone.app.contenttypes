# -*- coding: utf-8 -*-
from Acquisition import aq_base
from Products.CMFPlone.PloneBatch import Batch
from Products.CMFPlone.utils import safe_callable
from Products.Five import BrowserView
from plone.app.contenttypes import _
from plone.app.contenttypes.interfaces import IFolder
from plone.app.contenttypes.interfaces import IImage
from plone.event.interfaces import IEvent
from plone.memoize.view import memoize
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.contentprovider.interfaces import IContentProvider
import random

HAS_SECURITY_SETTINGS = True
try:
    from Products.CMFPlone.interfaces import ISecuritySchema
except ImportError:
    HAS_SECURITY_SETTINGS = False


class FolderView(BrowserView):

    def __init__(self, context, request):
        super(FolderView, self).__init__(context, request)

        self.plone_view = getMultiAdapter(
            (context, request), name=u"plone")
        self.portal_state = getMultiAdapter(
            (context, request), name=u"plone_portal_state")
        self.pas_member = getMultiAdapter(
            (context, request), name=u"pas_member")

        self.text_class = None

        limit_display = getattr(self.request, 'limit_display', None)
        limit_display = int(limit_display) if limit_display is not None else 20
        b_size = getattr(self.request, 'b_size', None)
        self.b_size = int(b_size) if b_size is not None else limit_display
        b_start = getattr(self.request, 'b_start', None)
        self.b_start = int(b_start) if b_start is not None else 0

    def results(self, **kwargs):
        """Return a content listing based result set with contents of the
        folder.

        :param **kwargs: Any keyword argument, which can be used for catalog
                         queries.
        :type  **kwargs: keyword argument

        :returns: plone.app.contentlisting based result set.
        :rtype: ``plone.app.contentlisting.interfaces.IContentListing`` based
                sequence.
        """
        # Extra filter
        kwargs.update(self.request.get('contentFilter', {}))
        if 'object_provides' not in kwargs:  # object_provides is more specific
            kwargs.setdefault('portal_type', self.friendly_types)
        kwargs.setdefault('batch', True)
        kwargs.setdefault('b_size', self.b_size)
        kwargs.setdefault('b_start', self.b_start)

        results = self.context.restrictedTraverse('@@folderListing')(**kwargs)
        return results

    def batch(self):
        batch = Batch(
            self.results(),
            size=self.b_size,
            start=self.b_start,
            orphan=1
        )
        return batch

    def normalizeString(self, text):
        return self.plone_view.normalizeString(text)

    def toLocalizedTime(self, time, long_format=None, time_only=None):
        return self.plone_view.toLocalizedTime(time, long_format, time_only)

    @property
    def friendly_types(self):
        return self.portal_state.friendly_types()

    @property
    def isAnon(self):
        return self.portal_state.anonymous()

    @property
    def navigation_root_url(self):
        return self.portal_state.navigation_root_url()

    @property
    def use_view_action(self):
        registry = getUtility(IRegistry)
        return registry.get('plone.types_use_view_action_in_listings', [])

    @property
    def show_about(self):
        if not HAS_SECURITY_SETTINGS:
            # BBB
            site_props = self.context.restrictedTraverse(
                'portal_properties').site_properties
            show_about = getattr(site_props, 'allowAnonymousViewAbout', False)
        else:
            registry = getUtility(IRegistry)
            settings = registry.forInterface(ISecuritySchema, prefix="plone")
            show_about = getattr(settings, 'allow_anon_views_about', False)
        return show_about or not self.isAnon

    @property
    def text(self):
        textfield = getattr(aq_base(self.context), 'text', None)
        text = getattr(textfield, 'output', None)
        if text:
            self.text_class = 'stx' if textfield.mimeType in (
                'text/structured', 'text/x-rst', 'text/restructured'
            ) else 'plain'
        return text

    @property
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

    def has_image(self, obj):
        if getattr(obj, 'getObject', False):
            obj = obj.getObject()
        img = getattr(aq_base(obj), 'image', None)
        return True if img else False

    def is_event(self, obj):
        if getattr(obj, 'getObject', False):
            obj = obj.getObject()
        return IEvent.providedBy(obj)

    def formatted_date(self, item):
        provider = getMultiAdapter(
            (self.context, self.request, self),
            IContentProvider, name='formatted_date'
        )
        return provider(item)

    @property
    @memoize
    def album_images(self):
        """Get all images within this folder.
        """
        images = self.results(
            batch=False,
            object_provides=IImage.__identifier__
        )
        return images

    @property
    @memoize
    def album_folders(self):
        """Get all folders within this folder.
        """
        images = self.results(
            batch=False,
            object_provides=IFolder.__identifier__
        )
        return images

    @property
    def album_random_image(self):
        """Get random image from this folder.
        """
        img = None
        images = self.album_images
        if images:
            img = random.choice(images)
        return img

    @property
    def album_number_images(self):
        """Get number of images from this folder.
        """
        images = self.album_images
        return len(images)

    @property
    def no_items_message(self):
        return _(
            'description_no_items_in_folder',
            default=u"There are currently no items in this folder."
        )
