# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING  # noqa
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from io import BytesIO
from zope.publisher.browser import TestRequest
from ZPublisher.HTTPResponse import HTTPResponse

import os.path
import pkg_resources
import unittest


HAS_ZSERVER = True
try:
    dist = pkg_resources.get_distribution('ZServer')
except pkg_resources.DistributionNotFound:
    HAS_ZSERVER = False


class DAVTestRequest(TestRequest):
    """Mock webdav request."""

    get_header = TestRequest.getHeader

    def _createResponse(self):
        return HTTPResponse()


class WebDAVIntegrationTest(unittest.TestCase):
    """Test webdav support."""

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Image', 'image')
        self.image = self.portal['image']
        self.image.title = 'My Image'
        self.portal.invokeFactory('File', 'file')
        self.file = self.portal['file']
        self.file.title = 'My file'

    def test_image_put(self):
        """Upload an image through webdav."""
        filename = os.path.join(os.path.dirname(__file__), u'image.jpg')
        with open(filename, 'rb') as myfile:
            request = DAVTestRequest(environ={
                'BODYFILE': myfile,
                'PATH_INFO': '/foo/bar/image.jpg',
            })
            self.image.REQUEST = request
            self.image.PUT()
        self.assertEqual(self.image.image.filename, u'image.jpg')
        self.assertEqual(self.image.get_size(), 5131)
        self.assertEqual(self.image.content_type(), 'image/jpeg')

    def test_file_put(self):
        """Upload a file through webdav."""
        filename = os.path.join(os.path.dirname(__file__), u'file.pdf')
        with open(filename, 'rb') as myfile:
            request = DAVTestRequest(environ={
                'BODYFILE': myfile,
                'PATH_INFO': '/foo/bar/file.pdf',
            })
            self.file.REQUEST = request
            self.file.PUT()
        self.assertEqual(self.file.file.filename, u'file.pdf')
        self.assertEqual(self.file.get_size(), 8561)
        self.assertEqual(self.file.content_type(), 'application/pdf')

    @unittest.skipIf(not HAS_ZSERVER, 'RFC822 not supported without ZServer')
    def test_image_put_rfc822(self):
        """Upload an image through webdav/rfc822."""
        filename = os.path.join(os.path.dirname(__file__), u'image.jpg')
        body = BytesIO()
        body.write(b"""title: My image
Content-Type: image/jpeg
Content-Disposition: attachment; filename*="utf-8''image.jpg"
Portal-Type: Image

""" + open(filename, 'rb').read()
        )
        body.seek(0)
        request = DAVTestRequest(environ={
            'BODYFILE': body,
            'PATH_INFO': '/foo/bar/image.jpg',
        })
        self.image.REQUEST = request
        self.image.PUT()
        self.assertEqual(self.image.image.filename, u'image.jpg')
        self.assertEqual(self.image.get_size(), 5131)
        self.assertEqual(self.image.content_type(), 'image/jpeg')

    @unittest.skipIf(not HAS_ZSERVER, 'RFC822 not supported without ZServer')
    def test_file_put_rfc822(self):
        """Upload a file through webdav/rfc822."""
        filename = os.path.join(os.path.dirname(__file__), u'file.pdf')
        body = BytesIO()
        body.write(b"""title: My file
Content-Type: application/pdf
Content-Disposition: attachment; filename*="utf-8''file.pdf"
Portal-Type: File

""" + open(filename, 'rb').read()
        )
        body.seek(0)
        request = DAVTestRequest(environ={
            'BODYFILE': body,
            'PATH_INFO': '/foo/bar/file.pdf',
        })
        self.file.REQUEST = request
        self.file.PUT()
        self.assertEqual(self.file.file.filename, u'file.pdf')
        self.assertEqual(self.file.get_size(), 8561)
        self.assertEqual(self.file.content_type(), 'application/pdf')
