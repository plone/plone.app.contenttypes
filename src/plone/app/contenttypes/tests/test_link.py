from plone.app.contenttypes.interfaces import ILink
from plone.app.contenttypes.testing import (  # noqa
    PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING,
)
from plone.app.contenttypes.testing import (  # noqa
    PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING,
)
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.z3cform.converters import LinkWidgetDataConverter
from plone.app.z3cform.widgets.link import LinkWidget
from plone.dexterity.interfaces import IDexterityFTI
from plone.testing.zope import Browser
from plone.uuid.interfaces import IUUID
from zope.component import createObject
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.schema import TextLine

import unittest


class LinkIntegrationTest(unittest.TestCase):
    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.request["ACTUAL_URL"] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name="Link")
        schema = fti.lookupSchema()
        self.assertTrue(schema.getName().endswith("_0_Link"))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name="Link")
        self.assertNotEqual(None, fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name="Link")
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(ILink.providedBy(new_object))

    def test_adding(self):
        self.portal.invokeFactory("Link", "doc1")
        self.assertTrue(ILink.providedBy(self.portal["doc1"]))


class LinkFunctionalTest(unittest.TestCase):
    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization",
            "Basic {}:{}".format(
                SITE_OWNER_NAME,
                SITE_OWNER_PASSWORD,
            ),
        )

    def test_add_link(self):
        self.browser.open(self.portal_url)
        self.browser.getLink("Link").click()
        self.browser.getControl(name="form.widgets.IDublinCore.title").value = "My link"
        self.browser.getControl(name="form.widgets.IDublinCore.description").value = (
            "This is my link."
        )
        self.browser.getControl(name="form.widgets.IShortName.id").value = (
            "my-special-link"
        )
        self.browser.getControl(name="form.widgets.remoteUrl.external").value = (
            "https://plone.org"
        )
        self.browser.getControl("Save").click()

        self.assertTrue(self.browser.url.endswith("my-special-link/view"))
        self.assertTrue("My link" in self.browser.contents)
        self.assertTrue("This is my link" in self.browser.contents)


class LinkWidgetIntegrationTest(unittest.TestCase):
    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    default_result = {
        "internal": "",
        "external": "",
        "email": "",
        "email_subject": "",
    }

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.request["ACTUAL_URL"] = self.portal.absolute_url()
        self.response = self.request.response
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        lid = self.portal.invokeFactory(
            "Link", "link", title="My Link", description="This is my link."
        )
        self.link = self.portal[lid]
        self.link_field = TextLine()
        self.widget = LinkWidget(self.request)

    def test_dc_towidget_external(self):
        url = "http://www.example.org"
        self.link.remoteUrl = url

        converter = LinkWidgetDataConverter(self.link_field, self.widget)
        expected = self.default_result.copy()
        expected["external"] = url
        self.assertEqual(converter.toWidgetValue(url), expected)

    def test_dc_towidget_internal(self):
        self.portal.invokeFactory(
            "Document", "doc1", title="A document", description="This is a document."
        )
        doc1 = self.portal["doc1"]
        url = doc1.absolute_url()
        converter = LinkWidgetDataConverter(self.link_field, self.widget)
        expected = self.default_result.copy()
        expected["internal"] = IUUID(doc1)
        self.assertEqual(converter.toWidgetValue(url), expected)

    def test_dc_towidget_mail(self):
        url = "mailto:foo@.example.org"
        converter = LinkWidgetDataConverter(self.link_field, self.widget)
        expected = self.default_result.copy()
        expected["email"] = url[7:]  # mailto is cut
        self.assertEqual(converter.toWidgetValue(url), expected)

    def test_dc_towidget_mail_subject(self):
        url = "mailto:foo@.example.org?subject=A subject"
        converter = LinkWidgetDataConverter(self.link_field, self.widget)
        expected = self.default_result.copy()
        expected["email"] = "foo@.example.org"
        expected["email_subject"] = "A subject"
        self.assertEqual(converter.toWidgetValue(url), expected)

    def test_dc_illegal(self):
        url = "foo"
        converter = LinkWidgetDataConverter(self.link_field, self.widget)
        expected = self.default_result.copy()
        expected["external"] = url
        self.assertEqual(converter.toWidgetValue(url), expected)

    def test_dc_var(self):
        url = "${portal_url}/foo"
        converter = LinkWidgetDataConverter(self.link_field, self.widget)
        expected = self.default_result.copy()
        expected["external"] = url
        self.assertEqual(converter.toWidgetValue(url), expected)

    def test_var_replacement_in_view(self):
        view = getMultiAdapter((self.link, self.request), name="link_redirect_view")

        self.link.remoteUrl = "${portal_url}"
        self.assertEqual(view.url(), "/plone")
        self.assertEqual(view.absolute_target_url(), "http://nohost/plone")

        self.link.remoteUrl = "${navigation_root_url}"
        self.assertEqual(view.url(), "/plone")
        self.assertEqual(view.absolute_target_url(), "http://nohost/plone")

    def test_resolve_uid_to_absolute_target(self):
        view = getMultiAdapter((self.link, self.request), name="link_redirect_view")

        self.portal.invokeFactory(
            "Document", "doc1", title="A document", description="This is a document."
        )
        doc1 = self.portal["doc1"]
        uid = IUUID(doc1)

        portal_state = getMultiAdapter(
            (self.link, self.request), name="plone_portal_state"
        )
        portal_url = portal_state.portal_url()

        # check an internal link
        self.link.remoteUrl = f"${{portal_url}}/resolveuid/{uid}"
        self.assertEqual(view.absolute_target_url(), f"{portal_url}/doc1")

        # check an internal link with fragment
        self.link.remoteUrl = f"${{portal_url}}/resolveuid/{uid}#autotoc-item-autotoc-1"
        self.assertEqual(
            view.absolute_target_url(), f"{portal_url}/doc1#autotoc-item-autotoc-1"
        )

        # check not resolvable uid
        self.link.remoteUrl = "/resolveuid/abc123"
        self.assertEqual(view.absolute_target_url(), "/resolveuid/abc123")
