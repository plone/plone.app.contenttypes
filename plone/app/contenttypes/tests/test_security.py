from io import BytesIO
from plone.app.contenttypes.testing import (  # noqa
    PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING,
)
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.testing.zope import Browser

import base64
import os
import pkg_resources
import re
import sys
import transaction
import unittest


# List various possibly read methods.
# Not all classes have all of them.
# Some may be inherited.
READ_METHODS = (
    "content_type",
    "Format",
    "get_size",
    "getFoldersAndImages",
    "getQuery",
    "getRawQuery",
    "index_html",
    "listMetaDataFields",
    "manage_DAVget",
    "manage_FTPget",
    "queryCatalog",
    "results",
    "selectedViewFields",
)
WRITE_METHODS = ("setQuery", "setSort_on", "setSort_reversed", "PUT")


class ResponseWrapper:
    """Decorates a response object with additional introspective methods."""

    _bodyre = re.compile("\r\n\r\n(.*)", re.MULTILINE | re.DOTALL)

    def __init__(self, response, outstream, path):
        self._response = response
        self._outstream = outstream
        self._path = path

    def __getattr__(self, name):
        return getattr(self._response, name)

    def getOutput(self):
        """Returns the complete output, headers and all."""
        return self._outstream.getvalue()

    def getBody(self):
        """Returns the page body, i.e. the output par headers."""
        body = self._bodyre.search(self.getOutput())
        if body is not None:
            body = body.group(1)
        return body

    def getPath(self):
        """Returns the path used by the request."""
        return self._path

    def getHeader(self, name):
        """Returns the value of a response header."""
        return self.headers.get(name.lower())

    def getCookie(self, name):
        """Returns a response cookie."""
        return self.cookies.get(name)


class TestSecurity(unittest.TestCase):
    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        # self.request['ACTUAL_URL'] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def publish(
        self,
        path,
        basic=None,
        env=None,
        extra=None,
        request_method="GET",
        stdin=None,
        handle_errors=True,
    ):
        """
        Mostly pulled from Testing.functional
        """
        # Note: the next import fail in Python 3, because it needs ZServer.
        from ZPublisher.Publish import publish_module
        from ZPublisher.Request import Request
        from ZPublisher.Response import Response

        transaction.commit()

        if env is None:
            env = {}

        env["SERVER_NAME"] = self.request["SERVER_NAME"]
        env["SERVER_PORT"] = self.request["SERVER_PORT"]
        env["REQUEST_METHOD"] = request_method

        p = path.split("?")
        if len(p) == 1:
            env["PATH_INFO"] = p[0]
        elif len(p) == 2:
            [env["PATH_INFO"], env["QUERY_STRING"]] = p
        else:
            raise TypeError("")

        if basic:
            env["HTTP_AUTHORIZATION"] = "Basic %s" % base64.encodestring(basic)

        if stdin is None:
            stdin = BytesIO()

        outstream = BytesIO()
        response = Response(stdout=outstream, stderr=sys.stderr)
        request = Request(stdin, env, response)

        publish_module(
            "Zope2", debug=not handle_errors, request=request, response=response
        )

        return ResponseWrapper(response, outstream, path)

    def test_put_gives_401(self):
        try:
            # pkg_resources.get_distribution("ZServer") is not good enough,
            # because ZServer may be included in the Zope2 package.
            import ZServer  # noqa
        except ImportError:
            print("Ignoring PUT request method tests, as we miss the ZServer.")
            return

        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory("Collection", id="collection")
        self.portal.invokeFactory("Document", id="page")
        self.portal.invokeFactory("File", id="file")
        self.portal.invokeFactory("Folder", id="folder")
        self.portal.invokeFactory("Image", id="image")
        collection = self.portal.collection
        fi = self.portal.file
        folder = self.portal.folder
        image = self.portal.image
        page = self.portal.page
        logout()

        # from zope.publisher.browser import TestRequest

        # import pdb; pdb.set_trace()
        # request = TestRequest(request_method="PUT")
        # collection.REQUEST = request
        # x = collection()

        path = "/" + collection.absolute_url(relative=True)
        response = self.publish(path=path, env={}, request_method="PUT")
        self.assertEqual(response.getStatus(), 401)

        path = "/" + fi.absolute_url(relative=True)
        response = self.publish(path=path, env={}, request_method="PUT")
        self.assertEqual(response.getStatus(), 401)

        path = "/" + folder.absolute_url(relative=True)
        response = self.publish(path=path, env={}, request_method="PUT")
        self.assertEqual(response.getStatus(), 401)

        path = "/" + image.absolute_url(relative=True)
        response = self.publish(path=path, env={}, request_method="PUT")
        self.assertEqual(response.getStatus(), 401)

        path = "/" + page.absolute_url(relative=True)
        response = self.publish(path=path, env={}, request_method="PUT")
        self.assertEqual(response.getStatus(), 401)

    def DISABLED_test_listDAVobjects_gives_401(self):
        # This actually gives 302, both with and without the patch.  It is
        # protected with AccessControl.Permissions.webdav_access.
        login(self.portal, TEST_USER_NAME)
        # only defined for folderish items
        self.portal.invokeFactory("Folder", id="folder")
        folder = self.portal.folder
        logout()

        folder_path = "/" + folder.absolute_url(relative=True)
        path = folder_path + "/listDAVObjects"
        response = self.publish(path=path, env={}, request_method="GET")
        self.assertEqual(response.getStatus(), 401)

    def get_permission_mapping(self, klass):
        permissions = klass.__ac_permissions__
        mapping = {}
        for permission in permissions:
            # permission can have two or three items:
            # ('WebDAV access',
            #  ('PROPFIND', 'listDAVObjects', 'manage_DAVget'),
            #  ('Manager', 'Authenticated'))
            perm, methods = list(permission)[:2]
            for method in methods:
                mapping[method] = perm
        return mapping

    def _test_class_protected(self, klass):
        mapping = self.get_permission_mapping(klass)
        for method in READ_METHODS:
            if method in klass.__dict__.keys():
                self.assertEqual(
                    mapping.get(method),
                    "View",
                    f"Method {method} missing view protection",
                )
        for method in WRITE_METHODS:
            if method in klass.__dict__.keys():
                self.assertEqual(
                    mapping.get(method),
                    "Modify portal content",
                    f"Method {method} missing edit protection",
                )

    def testCollection_protected(self):
        try:
            from plone.app.contenttypes.content import Collection
        except ImportError:
            return
        self._test_class_protected(Collection)

    def testDocument_protected(self):
        try:
            from plone.app.contenttypes.content import Document
        except ImportError:
            return
        self._test_class_protected(Document)

    def testFile_protected(self):
        try:
            from plone.app.contenttypes.content import File
        except ImportError:
            return
        self._test_class_protected(File)

    def testImage_protected(self):
        try:
            from plone.app.contenttypes.content import Image
        except ImportError:
            return
        self._test_class_protected(Image)
