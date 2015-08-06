# -*- coding: utf-8 -*-
from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer
from plone.app.contenttypes.tests.robot.variables import TEST_FOLDER_ID
from plone.app.event.testing import PAEvent_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from plone.app.testing import applyProfile
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.testing import z2
from zope.configuration import xmlconfig
from zope.interface import alsoProvides
import pkg_resources


def set_browserlayer(request):
    """Set the BrowserLayer for the request.

    We have to set the browserlayer manually, since importing the profile alone
    doesn't do it in tests.
    """
    alsoProvides(request, IPloneAppContenttypesLayer)


class PloneAppContenttypes(PloneSandboxLayer):

    defaultBases = (PAEvent_FIXTURE, PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import plone.app.contenttypes
        xmlconfig.file(
            'configure.zcml',
            plone.app.contenttypes,
            context=configurationContext
        )

        import plone.app.event.dx
        self.loadZCML(package=plone.app.event.dx,
                      context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plone.app.contenttypes:default')

        mtr = portal.mimetypes_registry
        mime_doc = mtr.lookup('application/msword')[0]
        mime_doc.icon_path = 'custom.png'

        portal.acl_users.userFolderAddUser('admin',
                                           'secret',
                                           ['Manager'],
                                           [])
        login(portal, 'admin')
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.invokeFactory(
            "Folder",
            id=TEST_FOLDER_ID,
            title=u"Test Folder"
        )

    def tearDownPloneSite(self, portal):
        applyProfile(portal, 'plone.app.contenttypes:uninstall')


class PloneAppContenttypesMigration(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):

        # prepare installing Products.ATContentTypes
        import Products.ATContentTypes
        self.loadZCML(package=Products.ATContentTypes)

        z2.installProduct(app, 'Products.Archetypes')
        z2.installProduct(app, 'Products.ATContentTypes')
        z2.installProduct(app, 'plone.app.blob')

        # prepare installing plone.app.collection
        try:
            pkg_resources.get_distribution('plone.app.collection')
            z2.installProduct(app, 'plone.app.collection')
        except pkg_resources.DistributionNotFound:
            pass

        # prepare installing plone.app.contenttypes
        z2.installProduct(app, 'Products.DateRecurringIndex')

        import plone.app.contenttypes
        xmlconfig.file(
            'configure.zcml',
            plone.app.contenttypes,
            context=configurationContext
        )
        import plone.app.referenceablebehavior
        self.loadZCML(package=plone.app.referenceablebehavior)

    def tearDownZope(self, app):
        try:
            pkg_resources.get_distribution('plone.app.collection')
            z2.uninstallProduct(app, 'plone.app.collection')
        except pkg_resources.DistributionNotFound:
            pass
        z2.uninstallProduct(app, 'plone.app.blob')
        z2.uninstallProduct(app, 'Products.ATContentTypes')
        z2.uninstallProduct(app, 'Products.Archetypes')

    def setUpPloneSite(self, portal):
        # install Products.ATContentTypes manually if profile is available
        # (this is only needed for Plone >= 5)
        profiles = [x['id'] for x in portal.portal_setup.listProfileInfo()]
        if 'Products.ATContentTypes:default' in profiles:
            applyProfile(portal, 'Products.ATContentTypes:default')

        # enable old Topic
        portal.portal_types.Topic.global_allow = True

        # install plone.app.collections manually if profile is available
        # (this is only needed for Plone >= 5)
        if 'plone.app.collection:default' in profiles:
            applyProfile(portal, 'plone.app.collection:default')

        applyProfile(portal, 'plone.app.referenceablebehavior:default')


PLONE_APP_CONTENTTYPES_FIXTURE = PloneAppContenttypes()
PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_CONTENTTYPES_FIXTURE,),
    name="PloneAppContenttypes:Integration"
)
PLONE_APP_CONTENTTYPES_MIGRATION_FIXTURE = PloneAppContenttypesMigration()
PLONE_APP_CONTENTTYPES_MIGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_CONTENTTYPES_MIGRATION_FIXTURE,),
    name="PloneAppContenttypes:Migration"
)
PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_CONTENTTYPES_FIXTURE,),
    name="PloneAppContenttypes:Functional"
)
PLONE_APP_CONTENTTYPES_MIGRATION_FUNCTIONAL_FIXTURE = PloneAppContenttypesMigration()  # noqa
PLONE_APP_CONTENTTYPES_MIGRATION_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_CONTENTTYPES_MIGRATION_FUNCTIONAL_FIXTURE,),
    name="PloneAppContenttypes:Migration_Functional"
)
PLONE_APP_CONTENTTYPES_ROBOT_TESTING = FunctionalTesting(
    bases=(
        PLONE_APP_CONTENTTYPES_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name="PloneAppContenttypes:Robot"
)
