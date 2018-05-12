# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING  # noqa
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.publisher.browser import TestRequest
from ZPublisher.HTTPResponse import HTTPResponse

import os.path
import unittest


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
        request = DAVTestRequest(environ={
            'BODYFILE': open(filename, 'rb'),
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
        request = DAVTestRequest(environ={
            'BODYFILE': open(filename, 'rb'),
            'PATH_INFO': '/foo/bar/file.pdf',
        })
        self.file.REQUEST = request
        self.file.PUT()
        self.assertEqual(self.file.file.filename, u'file.pdf')
        self.assertEqual(self.file.get_size(), 8561)
        self.assertEqual(self.file.content_type(), 'application/pdf')
