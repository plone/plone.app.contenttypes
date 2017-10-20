# -*- coding: utf-8 -*-
from plone import api
from plone.app.contenttypes.behaviors.leadimage import ILeadImageSettings
from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING  # noqa
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING  # noqa
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.fti import DexterityFTI
from plone.testing.z2 import Browser
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.viewlet.interfaces import IViewletManager

import io
import os
import unittest


class LeadImageBehaviorFunctionalTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = DexterityFTI('leadimagefolder')
        self.portal.portal_types._setObject('leadimagefolder', fti)
        fti.klass = 'plone.dexterity.content.Container'
        fti.behaviors = (
            'plone.app.contenttypes.behaviors.leadimage.ILeadImage',
        )
        self.fti = fti
        alsoProvides(self.portal.REQUEST, IPloneAppContenttypesLayer)
        alsoProvides(self.request, IPloneAppContenttypesLayer)
        from plone.app.contenttypes.behaviors.leadimage import ILeadImage
        alsoProvides(self.request, ILeadImage)
        self.portal.invokeFactory(
            'leadimagefolder',
            id='leadimagefolder',
            title=u'Folder with a lead image'
        )
        import transaction
        transaction.commit()
        # Set up browser
        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic {0}:{1}'.format(SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def test_lead_image_in_edit_form(self):
        self.browser.open(self.portal_url + '/leadimagefolder/edit')
        self.assertTrue('Lead Image' in self.browser.contents)
        self.assertTrue('Lead Image Caption' in self.browser.contents)

    def test_lead_image_viewlet_shows_up(self):
        self.browser.open(self.portal_url + '/leadimagefolder/edit')
        # Image upload
        file_path = os.path.join(os.path.dirname(__file__), 'image.jpg')
        file_ctl = self.browser.getControl(
            name='form.widgets.ILeadImage.image'
        )
        file_ctl.add_file(io.FileIO(file_path), 'image/png', 'image.jpg')
        # Image caption
        self.browser.getControl(
            name='form.widgets.ILeadImage.image_caption'
        ).value = 'My image caption'
        # Submit form
        self.browser.getControl('Save').click()

        self.assertTrue('My image caption' in self.browser.contents)
        self.assertTrue('image.jpg' in self.browser.contents)

        self.assertTrue('<div class="leadImage">' in self.browser.contents)

        # But doesn't show up on folder_contents, which is not a default view
        self.browser.open(self.portal_url + '/leadimagefolder/folder_contents')
        self.assertTrue('<div class="leadImage">' not in self.browser.contents)


class LeadImageBehaviorIntegrationtTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = DexterityFTI('leadimagefolder')
        self.portal.portal_types._setObject('leadimagefolder', fti)
        fti.klass = 'plone.dexterity.content.Container'
        fti.behaviors = (
            'plone.app.contenttypes.behaviors.leadimage.ILeadImage',
        )
        self.fti = fti
        alsoProvides(self.portal.REQUEST, IPloneAppContenttypesLayer)
        alsoProvides(self.request, IPloneAppContenttypesLayer)
        from plone.app.contenttypes.behaviors.leadimage import ILeadImage
        alsoProvides(self.request, ILeadImage)
        self.portal.invokeFactory(
            'leadimagefolder',
            id='leadimagefolder',
            title=u'Folder with a lead image'
        )

    def test_lead_image_viewlet_settings(self):
        is_visible = api.portal.get_registry_record(
            'is_visible',
            interface=ILeadImageSettings)
        self.assertTrue(is_visible)

        api.portal.set_registry_record(
            'is_visible',
            False,
            interface=ILeadImageSettings)
        is_visible = api.portal.get_registry_record(
            'is_visible',
            interface=ILeadImageSettings)
        self.assertFalse(is_visible)

        scale_name = api.portal.get_registry_record(
            'scale_name',
            interface=ILeadImageSettings)
        self.assertEqual(scale_name, 'mini')

    def test_lead_image_preferences(self):
        container = api.content.get('/leadimagefolder')

        # Image upload
        file_path = os.path.join(os.path.dirname(__file__), "image.jpg")
        add_leadimage_from_file_path(container, file_path)

        self.request.set('URL', container.absolute_url())
        self.request.set('ACTUAL_URL', container.absolute_url())

        view = container.restrictedTraverse('view')
        view.update()
        self.assertTrue(
            'figure class="leadImageContainer"' in view.render(),
            'Leadimage should be visible.')

        api.portal.set_registry_record(
            'is_visible',
            False,
            interface=ILeadImageSettings)
        view.update()
        self.assertTrue(
            'class="leadImageContainer"' not in view.render(),
            'Leadimage should not be visible.')

    def test_lead_image_viewlet_view(self):
        container = api.content.get('/leadimagefolder')

        # Image upload
        file_path = os.path.join(os.path.dirname(__file__), "image.jpg")
        add_leadimage_from_file_path(container, file_path)

        self.request.set('URL', container.absolute_url())
        self.request.set('ACTUAL_URL', container.absolute_url())

        view = container.restrictedTraverse('view')
        view.update()
        self.assertTrue(view.render())

        manager_name = 'plone.abovecontenttitle'
        manager = queryMultiAdapter(
            (container, self.request, view),
            IViewletManager, manager_name, default=None)
        self.assertIsNotNone(manager)
        manager.update()
        viewlet = [v for v in manager.viewlets
                   if v.__name__ == 'contentleadimage']
        self.assertEqual(len(viewlet), 1)

        lead_viewlet = viewlet[0]
        self.assertEqual(lead_viewlet.scale_name, 'mini')
        self.assertTrue(lead_viewlet.available)
        is_visible = api.portal.set_registry_record(
            'is_visible',
            False,
            interface=ILeadImageSettings)
        self.assertFalse(is_visible)


def add_leadimage_from_file_path(obj, file_path):
    file_name = file_path.split(os.sep)[-1]
    if not obj.hasObject(file_name):
        from plone.namedfile.file import NamedBlobImage
        namedblobimage = NamedBlobImage(
            data=open(file_path, 'r').read(),
            filename=unicode(file_name)
        )
        image = api.content.create(type='Image',
                                   title=file_name,
                                   image=namedblobimage,
                                   container=api.portal.get(),
                                   language='fr')
        image.setTitle(file_name)
        image.reindexObject()
        setattr(obj, 'image', namedblobimage)
