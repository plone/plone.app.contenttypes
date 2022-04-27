from Acquisition import aq_inner
from plone.memoize.view import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.MimetypesRegistry.MimeTypeItem import guess_icon_path
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


PREFIX = "++resource++mimetype.icons/"


class IUtils(Interface):
    """ """

    def getMimeTypeIcon(content_file):
        """ """


@implementer(IUtils)
class Utils(BrowserView):
    def _get_mimes(self, content_file):
        # We use 'yield' so iteration can be cut short
        # if the calling code is happy.
        context = aq_inner(self.context)
        mtr = getToolByName(context, "mimetypes_registry")
        if content_file.contentType:
            # this gives a tuple
            yield from mtr.lookup(content_file.contentType)
        if content_file.filename:
            # this gives a single mime type
            yield mtr.lookupExtension(content_file.filename)
        yield from mtr.lookup("application/octet-stream")

    @memoize
    def getMimeTypeIcon(self, content_file):
        # Get possible mime types, and try to find an icon path.
        # Keep the first one, in case there is no good match.
        first = None
        for mime in self._get_mimes(content_file):
            if first is None:
                first = mime
            if hasattr(mime, "icon_path"):
                icon_path = mime.icon_path
                if not icon_path.startswith("++"):
                    icon_path = PREFIX + icon_path
                return icon_path

        if first is None:
            # Probably does not happen in practice.
            return ""
        context = aq_inner(self.context)
        pstate = getMultiAdapter((context, self.request), name="plone_portal_state")
        portal_url = pstate.portal_url()
        return portal_url + "/" + guess_icon_path(first)
