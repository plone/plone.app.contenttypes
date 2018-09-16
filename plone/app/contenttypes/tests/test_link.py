# -*- coding: utf-8 -*-
from datetime import datetime
from plone.app.z3cform.converters import LinkWidgetDataConverter
from plone.app.z3cform.widget import LinkWidget
from plone.app.contenttypes.interfaces import ILink
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING  # noqa
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING  # noqa
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.dexterity.interfaces import IDexterityFTI
from plone.testing.z2 import Browser
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from zope.component import createObject
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.event import notify
from zope.interface import alsoProvides
from zope.schema import TextLine
from zope.traversing.interfaces import BeforeTraverseEvent

import unittest


class LinkIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])

    def test_schema(self):
        fti = queryUtility(
            IDexterityFTI,
            name='Link')
        schema = fti.lookupSchema()
        self.assertEqual(schema.getName(), 'plone_0_Link')

    def test_fti(self):
        fti = queryUtility(
            IDexterityFTI,
            name='Link'
        )
        self.assertNotEqual(None, fti)

    def test_factory(self):
        fti = queryUtility(
            IDexterityFTI,
            name='Link'
        )
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(ILink.providedBy(new_object))

    def test_adding(self):
        self.portal.invokeFactory(
            'Link',
            'doc1'
        )
        self.assertTrue(ILink.providedBy(self.portal['doc1']))


class LinkViewIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        self.response = self.request.response
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Link', 'link')
        link = self.portal['link']
        link.title = 'My Link'
        link.description = 'This is my link.'
        self.link = link
        self.request.set('URL', link.absolute_url())
        self.request.set('ACTUAL_URL', link.absolute_url())
        alsoProvides(self.request, IPloneFormLayer)

        # setup manually the correct browserlayer, see:
        # https://dev.plone.org/ticket/11673
        notify(BeforeTraverseEvent(self.portal, self.request))

    def test_link_redirect_view(self):
        view = self.link.restrictedTraverse('@@view')
        self.assertTrue(view())
        self.assertEqual(view.request.response.status, 200)
        self.assertTrue('My Link' in view())
        self.assertTrue('This is my link.' in view())

    def test_link_redirect_view_external_url(self):
        self.link.remoteUrl = 'http://www.plone.org'
        self._publish(self.link)
        view = self._get_link_redirect_view(self.link)

        # As manager: do not redirect
        self.assertTrue(view())
        self.assertEqual(self.response.status, 200)

        # As anonymous: redirect
        logout()
        self.assertTrue(view())
        self._assert_redirect('http://www.plone.org')

    def test_link_redirect_view_absolute_path(self):
        self.link.remoteUrl = '/plone/my-folder/my-item'
        self._publish(self.link)
        view = self._get_link_redirect_view(self.link)

        # As manager: do not redirect
        self.assertTrue(view())
        self.assertEqual(self.response.status, 200)

        # As anonymous: redirect
        logout()
        self.assertTrue(view())
        self._assert_redirect('http://nohost/plone/my-folder/my-item')

    def test_link_redirect_view_relative_path(self):
        self.link.remoteUrl = '../my-item'
        self._publish(self.link)
        view = self._get_link_redirect_view(self.link)

        # As manager: do not redirect
        self.assertTrue(view())
        self.assertEqual(self.response.status, 200)

        # As anonymous: redirect
        logout()
        self.assertTrue(view())
        # The following URL will be redirected to:
        # "http://nohost/plone/my-item"
        self._assert_redirect('http://nohost/plone/link/../my-item')

    def test_link_redirect_view_path_with_variable(self):
        self.link.remoteUrl = '${navigation_root_url}/my-folder/my-item'
        self._publish(self.link)
        view = self._get_link_redirect_view(self.link)

        # As manager: do not redirect
        self.assertTrue(view())
        self.assertEqual(self.response.status, 200)

        # As anonymous: redirect
        logout()
        self.assertTrue(view())
        self._assert_redirect('http://nohost/plone/my-folder/my-item')

        # Should give the same result with ${portal_url}
        self.link.remoteUrl = '${portal_url}/my-folder/my-item'
        self.assertTrue(view())
        self._assert_redirect('http://nohost/plone/my-folder/my-item')

    def test_link_redirect_view_path_with_variable_and_parameters(self):
        # https://github.com/plone/plone.app.contenttypes/issues/457
        self.link.remoteUrl = '${portal_url}/@@search?SearchableText=Plone'
        self._publish(self.link)
        view = self._get_link_redirect_view(self.link)

        # As manager: do not redirect
        self.assertTrue(view())
        self.assertEqual(self.response.status, 200)

        # As anonymous: redirect
        logout()
        self.assertTrue(view())
        self._assert_redirect(
            'http://nohost/plone/@@search?SearchableText=Plone',
        )

    def test_mailto_type(self):
        self.link.remoteUrl = 'mailto:stress@test.us'
        view = self._get_link_redirect_view(self.link)
        self._publish(self.link)
        logout()
        rendered = view()
        self.assertIn('href="mailto:stress@test.us"', rendered)
        self._assert_response_OK()

    def test_tel_type(self):
        self.link.remoteUrl = 'tel:123'
        view = self._get_link_redirect_view(self.link)
        self._publish(self.link)
        logout()
        rendered = view()
        self.assertIn('href="tel:123"', rendered)
        self._assert_response_OK()

    def test_callto_type(self):
        self.link.remoteUrl = 'callto:123'
        view = self._get_link_redirect_view(self.link)
        self._publish(self.link)
        logout()
        rendered = view()
        self.assertIn('href="callto:123"', rendered)
        self._assert_response_OK()

    def test_webdav_type(self):
        self.link.remoteUrl = 'webdav://web.site/resource'
        view = self._get_link_redirect_view(self.link)
        self._publish(self.link)
        logout()
        rendered = view()
        self.assertIn(
            'href="webdav://web.site/resource"',
            rendered
        )
        self._assert_response_OK()

    def test_caldav_type(self):
        self.link.remoteUrl = 'caldav://calendar.site/resource'
        view = self._get_link_redirect_view(self.link)
        self._publish(self.link)
        logout()
        rendered = view()
        self.assertIn(
            'href="caldav://calendar.site/resource"',
            rendered
        )
        self._assert_response_OK()

    def test_file_type(self):
        self.link.remoteUrl = 'file:///some/file/on/your/system'
        view = self._get_link_redirect_view(self.link)
        self._publish(self.link)
        logout()
        self.assertTrue(view())
        self._assert_redirect(self.link.remoteUrl)

    def test_ftp_type(self):
        self.link.remoteUrl = 'ftp://thereIsNoSuchDomain.isThere{0}'.format(
            datetime.now().isoformat()
        )
        view = self._get_link_redirect_view(self.link)
        self._publish(self.link)
        logout()
        self.assertTrue(view())
        self._assert_redirect(self.link.remoteUrl)

    def _publish(self, obj):
        portal_workflow = getToolByName(self.portal, 'portal_workflow')
        portal_workflow.doActionFor(obj, 'publish')

    def _assert_redirect(self, url):
        self.assertEqual(self.response.status, 302)
        self.assertEqual(self.response.headers['location'], url)

    def _assert_response_OK(self):
        self.assertEqual(self.response.status, 200)

    def _get_link_redirect_view(self, obj):
        return getMultiAdapter((obj, self.request), name='link_redirect_view')


class LinkFunctionalTest(unittest.TestCase):

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
            'Basic {0}:{1}'.format(SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def test_add_link(self):
        self.browser.open(self.portal_url)
        self.browser.getLink('Link').click()
        self.browser.getControl(name='form.widgets.IDublinCore.title')\
            .value = 'My link'
        self.browser.getControl(name='form.widgets.IDublinCore.description')\
            .value = 'This is my link.'
        self.browser.getControl(name='form.widgets.IShortName.id')\
            .value = 'my-special-link'
        self.browser.getControl(name='form.widgets.remoteUrl.external')\
            .value = 'https://plone.org'
        self.browser.getControl('Save').click()

        self.assertTrue(self.browser.url.endswith('my-special-link/view'))
        self.assertTrue('My link' in self.browser.contents)
        self.assertTrue('This is my link' in self.browser.contents)


class LinkWidgetIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    default_result = {'internal': u'',
                      'external': u'',
                      'email': u'',
                      'email_subject': u''}

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        self.response = self.request.response
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        lid = self.portal.invokeFactory('Link', 'link',
                                        title='My Link',
                                        description="This is my link.")
        self.link = self.portal[lid]
        self.link_field = TextLine()
        self.widget = LinkWidget(self.request)

    def test_dc_towidget_external(self):
        url = 'http://www.example.org'
        self.link.remoteUrl = url

        converter = LinkWidgetDataConverter(self.link_field, self.widget)
        expected = self.default_result.copy()
        expected['external'] = url
        self.assertEqual(converter.toWidgetValue(url), expected)

    def test_dc_towidget_internal(self):
        self.portal.invokeFactory('Document', 'doc1',
                                  title='A document',
                                  description="This is a document.")
        doc1 = self.portal['doc1']
        url = doc1.absolute_url()
        converter = LinkWidgetDataConverter(self.link_field, self.widget)
        expected = self.default_result.copy()
        expected['internal'] = IUUID(doc1)
        self.assertEqual(converter.toWidgetValue(url), expected)

    def test_dc_towidget_mail(self):
        url = u'mailto:foo@.example.org'
        converter = LinkWidgetDataConverter(self.link_field, self.widget)
        expected = self.default_result.copy()
        expected['email'] = url[7:]   # mailto is cut
        self.assertEqual(converter.toWidgetValue(url), expected)

    def test_dc_towidget_mail_subject(self):
        url = 'mailto:foo@.example.org?subject=A subject'
        converter = LinkWidgetDataConverter(self.link_field, self.widget)
        expected = self.default_result.copy()
        expected['email'] = u'foo@.example.org'
        expected['email_subject'] = u'A subject'
        self.assertEqual(converter.toWidgetValue(url), expected)

    def test_dc_illegal(self):
        url = 'foo'
        converter = LinkWidgetDataConverter(self.link_field, self.widget)
        expected = self.default_result.copy()
        expected['external'] = url
        self.assertEqual(converter.toWidgetValue(url), expected)

    def test_dc_var(self):
        url = '${portal_url}/foo'
        converter = LinkWidgetDataConverter(self.link_field, self.widget)
        expected = self.default_result.copy()
        expected['external'] = url
        self.assertEqual(converter.toWidgetValue(url), expected)

    def test_var_replacement_in_view(self):
        view = getMultiAdapter(
            (self.link, self.request),
            name='link_redirect_view'
        )

        self.link.remoteUrl = '${portal_url}'
        self.assertEqual(view.url(), '/plone')
        self.assertEqual(view.absolute_target_url(), 'http://nohost/plone')

        self.link.remoteUrl = '${navigation_root_url}'
        self.assertEqual(view.url(), '/plone')
        self.assertEqual(view.absolute_target_url(), 'http://nohost/plone')
