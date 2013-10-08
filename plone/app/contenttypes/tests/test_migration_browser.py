# -*- coding: utf-8 -*-
import unittest2 as unittest

from Products.CMFCore.utils import getToolByName

from zope.interface import directlyProvides

from plone.dexterity.fti import DexterityFTI

from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer

from plone.app.contenttypes.interfaces import (
    IDocument,
    IEvent,
    IFile,
    IFolder,
    IImage,
    ILink,
    INewsItem,
)

from plone.app.contenttypes.testing import \
    PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

from plone.app.testing import TEST_USER_ID, setRoles


class FixBaseclassesTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        self.request['URL'] = self.portal.absolute_url()
        directlyProvides(self.request, IPloneAppContenttypesLayer)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.catalog = getToolByName(self.portal, "portal_catalog")
        fti = DexterityFTI('mockobject')
        fti.klass = 'plone.dexterity.content.Item'
        self.portal.portal_types._setObject('mockobject', fti)
        self.portal.invokeFactory('mockobject', 'obj1')
        self.obj = self.portal.obj1

    def test_view_is_registered(self):
        view = self.portal.restrictedTraverse('fix_base_classes')
        self.assertTrue(isinstance(view(), str))

    def test_fix_interface_for_document(self):
        self.obj.portal_type = 'Document'
        self.catalog.reindexObject(self.obj)

        self.portal.restrictedTraverse('fix_base_classes')()

        self.assertTrue(IDocument.providedBy(self.obj))

    def test_fix_interface_for_event(self):
        self.obj.portal_type = 'Event'
        self.catalog.reindexObject(self.obj)

        self.portal.restrictedTraverse('fix_base_classes')()

        self.assertTrue(IEvent.providedBy(self.obj))

    def test_fix_interface_for_file(self):
        self.obj.portal_type = 'File'
        self.catalog.reindexObject(self.obj)

        self.portal.restrictedTraverse('fix_base_classes')()

        self.assertTrue(IFile.providedBy(self.obj))

    def test_fix_interface_for_folder(self):
        self.obj.portal_type = 'Folder'
        self.catalog.reindexObject(self.obj)

        self.portal.restrictedTraverse('fix_base_classes')()

        self.assertTrue(IFolder.providedBy(self.obj))

    def test_fix_interface_for_image(self):
        self.obj.portal_type = 'Image'
        self.catalog.reindexObject(self.obj)

        self.portal.restrictedTraverse('fix_base_classes')()

        self.assertTrue(IImage.providedBy(self.obj))

    def test_fix_interface_for_link(self):
        self.obj.portal_type = 'Link'
        self.catalog.reindexObject(self.obj)

        self.portal.restrictedTraverse('fix_base_classes')()

        self.assertTrue(ILink.providedBy(self.obj))

    def test_fix_interface_for_news_item(self):
        self.obj.portal_type = 'News Item'
        self.catalog.reindexObject(self.obj)

        self.portal.restrictedTraverse('fix_base_classes')()

        self.assertTrue(INewsItem.providedBy(self.obj))
