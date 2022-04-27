from plone.app.contenttypes.testing import (  # noqa
    PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING,
)
from zope.component import getMultiAdapter

import unittest


# The default fallback is the icon for 'application/octet-stream':
FALLBACK = "++resource++mimetype.icons/application.png"
# Most or all icons should have this as prefix:
PREFIX = "++resource++mimetype.icons/"


class DummyFile:
    """Dummy file object.

    For these tests, we only need a contentType and filename.
    """

    def __init__(self, contentType, filename):
        self.contentType = contentType
        self.filename = filename


class MimeTypeIconIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer["portal"]
        request = self.layer["request"]
        self.view = getMultiAdapter((portal, request), name="contenttype_utils")

    def test_none(self):
        self.assertEqual(self.view.getMimeTypeIcon(DummyFile(None, None)), FALLBACK)

    def test_unknown(self):
        self.assertEqual(
            self.view.getMimeTypeIcon(DummyFile("some/unknown", "unkown.unknown")),
            FALLBACK,
        )

    def test_contenttype_pdf(self):
        self.assertEqual(
            self.view.getMimeTypeIcon(DummyFile("application/pdf", None)),
            PREFIX + "pdf.png",
        )

    def test_filename_pdf(self):
        self.assertEqual(
            self.view.getMimeTypeIcon(DummyFile(None, "plone.pdf")), PREFIX + "pdf.png"
        )
