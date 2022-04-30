from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer
from plone.app.contenttypes.tests.robot.variables import TEST_FOLDER_ID
from plone.app.event.testing import PAEvent_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing import zope
from zope.interface import alsoProvides


def set_browserlayer(request):
    """Set the BrowserLayer for the request.

    We have to set the browserlayer manually, since importing the profile alone
    doesn't do it in tests.
    """
    alsoProvides(request, IPloneAppContenttypesLayer)


class PloneAppContenttypes(PloneSandboxLayer):

    defaultBases = (
        PAEvent_FIXTURE,
        PLONE_FIXTURE,
    )

    def setUpZope(self, app, configurationContext):
        import plone.app.contenttypes

        self.loadZCML(package=plone.app.contenttypes)
        import plone.app.event.dx

        self.loadZCML(package=plone.app.event.dx)

    def setUpPloneSite(self, portal):
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")


class PloneAppContenttypesRobot(PloneAppContenttypes):
    """Same as the default but with a added folder 'robot-test-folder'."""

    defaultBases = (PAEvent_FIXTURE, REMOTE_LIBRARY_BUNDLE_FIXTURE)

    def setUpPloneSite(self, portal):
        portal.acl_users.userFolderAddUser(
            SITE_OWNER_NAME, SITE_OWNER_PASSWORD, ["Manager"], []
        )
        login(portal, SITE_OWNER_NAME)
        super().setUpPloneSite(portal)
        portal.invokeFactory("Folder", id=TEST_FOLDER_ID, title="Test Folder")

    def tearDownPloneSite(self, portal):
        login(portal, "admin")
        portal.manage_delObjects([TEST_FOLDER_ID])
        super().tearDownPloneSite(portal)


PLONE_APP_CONTENTTYPES_FIXTURE = PloneAppContenttypes()
PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_CONTENTTYPES_FIXTURE,), name="PloneAppContenttypes:Integration"
)
PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_CONTENTTYPES_FIXTURE,), name="PloneAppContenttypes:Functional"
)
PLONE_APP_CONTENTTYPES_ROBOT_FIXTURE = PloneAppContenttypesRobot()
PLONE_APP_CONTENTTYPES_ROBOT_TESTING = FunctionalTesting(
    bases=(PLONE_APP_CONTENTTYPES_ROBOT_FIXTURE, zope.WSGI_SERVER_FIXTURE),
    name="PloneAppContenttypes:Robot",
)
