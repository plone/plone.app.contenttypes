# -*- coding: utf-8 -*-
import unittest2 as unittest

import os.path

from zope.interface import alsoProvides
from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser

from plone.app.contenttypes.interfaces import IFile

from plone.app.contenttypes.testing import (
    PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING,
    PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING
)

from plone.app.testing import TEST_USER_ID, setRoles
from plone.app.z3cform.interfaces import IPloneFormLayer

from plone.namedfile.file import NamedFile
from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer


class FileIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])

    def test_schema(self):
        fti = queryUtility(
            IDexterityFTI,
            name='File')
        schema = fti.lookupSchema()
        self.assertEqual(schema.getName(), 'plone_0_File')

    def test_fti(self):
        fti = queryUtility(
            IDexterityFTI,
            name='File'
        )
        self.assertNotEquals(None, fti)

    def test_factory(self):
        fti = queryUtility(
            IDexterityFTI,
            name='File'
        )
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(IFile.providedBy(new_object))

    def test_adding(self):
        self.portal.invokeFactory(
            'File',
            'doc1'
        )
        self.assertTrue(IFile.providedBy(self.portal['doc1']))

    def test_view(self):
        self.portal.invokeFactory('File', 'file')
        file1 = self.portal['file']
        file1.title = "My File"
        file1.description = "This is my file."
        self.request.set('URL', file1.absolute_url())
        self.request.set('ACTUAL_URL', file1.absolute_url())
        alsoProvides(self.request, IPloneFormLayer)
        view = file1.restrictedTraverse('@@view')

        self.assertTrue(view())
        self.assertEqual(view.request.response.status, 200)
        self.assertTrue('My File' in view())
        self.assertTrue('This is my file.' in view())

    def test_view_no_video_audio_tag(self):
        self.portal.invokeFactory('File', 'file')
        file = self.portal['file']
        file.file = NamedFile()
        file.file.contentType = 'application/pdf'
        alsoProvides(self.request, IPloneAppContenttypesLayer)
        view = file.restrictedTraverse('@@file_view')
        rendered = view()
        self.assertTrue('</audio>' not in rendered)
        self.assertTrue('</video>' not in rendered)

    def test_view_video_tag(self):
        self.portal.invokeFactory('File', 'file')
        file = self.portal['file']
        file.file = NamedFile()
        file.file.contentType = 'audio/mp3'
        alsoProvides(self.request, IPloneAppContenttypesLayer)
        view = file.restrictedTraverse('@@file_view')
        rendered = view()
        self.assertTrue('</audio>' in rendered)

    def test_view_audio_tag(self):
        self.portal.invokeFactory('File', 'file')
        file = self.portal['file']
        file.file = NamedFile()
        file.file.contentType = 'video/ogv'
        alsoProvides(self.request, IPloneAppContenttypesLayer)
        view = file.restrictedTraverse('@@file_view')
        rendered = view()
        self.assertTrue('</video>' in rendered)


class FileFunctionalTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def test_add_file(self):
        self.browser.open(self.portal_url)
        self.browser.getLink('File').click()
        self.browser.getControl(name='form.widgets.title')\
            .value = "My file"
        self.browser.getControl(name='form.widgets.description')\
            .value = "This is my file."
        file_path = os.path.join(os.path.dirname(__file__), "image.jpg")
        file_ctl = self.browser.getControl(name='form.widgets.file')
        file_ctl.add_file(open(file_path), 'image/png', 'image.jpg')
        self.browser.getControl('Save').click()
        self.assertTrue(self.browser.url.endswith('image.jpg/view'))
        self.assertTrue('My file' in self.browser.contents)
        self.assertTrue('This is my file' in self.browser.contents)

    def test_shortname_file(self):
        self.browser.open(self.portal_url)
        self.browser.getLink('File').click()
        self.browser.getControl(name='form.widgets.title')\
            .value = "My file"
        self.browser.getControl(name='form.widgets.IShortName.id')\
            .value = "my-special-file"
        file_path = os.path.join(os.path.dirname(__file__), "image.jpg")
        file_ctl = self.browser.getControl(name='form.widgets.file')
        file_ctl.add_file(open(file_path), 'image/png', 'image.jpg')
        self.browser.getControl('Save').click()
        self.assertTrue(self.browser.url.endswith('my-special-file/view'))

    def test_mime_icon_pdf_for_file_(self):
        self.browser.open(self.portal_url)
        self.browser.getLink('File').click()

        self.browser.getControl(name='form.widgets.title')\
            .value = "My file"
        self.browser.getControl(name='form.widgets.description')\
            .value = "This is my pdf file."
        file_path = os.path.join(os.path.dirname(__file__), "file.pdf")
        file_ctl = self.browser.getControl(name='form.widgets.file')
        file_ctl.add_file(open(file_path), 'application/pdf', 'file.pdf')
        self.browser.getControl('Save').click()
        self.assertTrue(self.browser.url.endswith('file.pdf/view'))
        self.assertTrue('pdf.png' in self.browser.contents)

    def test_alternative_mime_icon_doc_for_file(self):
        self.browser.open(self.portal_url)
        self.browser.getLink('File').click()

        self.browser.getControl(name='form.widgets.title')\
            .value = "My file"
        self.browser.getControl(name='form.widgets.description')\
            .value = "This is my doc file."
        file_path = os.path.join(os.path.dirname(__file__), "file.doc")
        file_ctl = self.browser.getControl(name='form.widgets.file')
        file_ctl.add_file(open(file_path), 'application/msword', 'file.doc')
        self.browser.getControl('Save').click()
        self.assertTrue(self.browser.url.endswith('file.doc/view'))
        self.assertTrue('custom.png' in self.browser.contents)

    def test_mime_icon_odt_for_file_(self):
        self.browser.open(self.portal_url)
        self.browser.getLink('File').click()

        self.browser.getControl(name='form.widgets.title')\
            .value = "My file"
        self.browser.getControl(name='form.widgets.description')\
            .value = "This is my odt file."
        file_path = os.path.join(os.path.dirname(__file__), "file.odt")
        file_ctl = self.browser.getControl(name='form.widgets.file')
        file_ctl.add_file(open(file_path),
                          'application/vnd.oasis.opendocument.text',
                          'file.odt')
        self.browser.getControl('Save').click()
        self.assertTrue(self.browser.url.endswith('file.odt/view'))
        self.assertTrue('application.png' in self.browser.contents)
