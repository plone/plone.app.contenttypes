from plone.app.contenttypes.browser.utils import Utils
from plone.base.utils import human_readable_size

import re


class FileView(Utils):
    def is_videotype(self):
        ct = self.context.file.contentType
        return "video/" in ct

    def is_audiotype(self):
        ct = self.context.file.contentType
        return "audio/" in ct

    def human_readable_size(self):
        return human_readable_size(self.context.file.getSize())

    def icon(self):
        if "text" in self.context.file.contentType:
            return "contenttype-text"
        if "html" in self.context.file.contentType:
            return "contenttype-text"
        if re.search(r"(archive|zip|compressed)", self.context.file.contentType):
            return "contenttype-archive"
        if "audio" in self.context.file.contentType:
            return "contenttype-audio"
        if "video" in self.context.file.contentType:
            return "contenttype-video"
        if "pdf" in self.context.file.contentType:
            return "contenttype-pdf"
        else:
            return "contenttype-file"
