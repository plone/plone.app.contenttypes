# -*- coding: utf-8 -*-
from plone.app.contenttypes.browser.utils import Utils


class FileView(Utils):

    def is_videotype(self):
        ct = self.context.file.contentType
        return 'video/' in ct

    def is_audiotype(self):
        ct = self.context.file.contentType
        return 'audio/' in ct

    def get_mimetype_icon(self):
        return super(FileView, self).getMimeTypeIcon(self.context.file)
