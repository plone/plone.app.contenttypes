# -*- coding: utf-8 -*-
from plone.app.contenttypes.browser.utils import Utils


class FileView(Utils):

    def __init__(self, context, request):
        super(FileView, self).__init__(context, request)

    def is_videotype(self):
        ct = self.context.file.contentType
        return 'video/' in ct

    def is_audiotype(self):
        ct = self.context.file.contentType
        return 'audio/' in ct

    def get_mimetype_icon(self):
        return super(FileView, self).getMimeTypeIcon(self.context.file)
