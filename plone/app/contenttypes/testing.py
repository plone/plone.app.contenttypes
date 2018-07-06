# -*- coding: utf-8 -*-
from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer
from plone.app.contenttypes.tests.robot.variables import TEST_FOLDER_ID
from plone.app.event.testing import PAEvent_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing import z2
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
        self.loadZCML(package=plone.app.contenttypes)
        import plone.app.event.dx
        self.loadZCML(package=plone.app.event.dx)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plone.app.contenttypes:default')
        portal.portal_workflow.setDefaultChain('simple_publication_workflow')

    def tearDownPloneSite(self, portal):
        applyProfile(portal, 'plone.app.contenttypes:uninstall')


class PloneAppContenttypesRobot(PloneAppContenttypes):
    """Same as the default but with a added folder 'robot-test-folder'.
    """

    defaultBases = (
        PAEvent_FIXTURE, REMOTE_LIBRARY_BUNDLE_FIXTURE)

    def setUpPloneSite(self, portal):
        portal.acl_users.userFolderAddUser(
            SITE_OWNER_NAME, SITE_OWNER_PASSWORD, ['Manager'], [])
        login(portal, SITE_OWNER_NAME)
        super(PloneAppContenttypesRobot, self).setUpPloneSite(portal)
        portal.invokeFactory('Folder', id=TEST_FOLDER_ID, title=u'Test Folder')

    def tearDownPloneSite(self, portal):
        login(portal, 'admin')
        portal.manage_delObjects([TEST_FOLDER_ID])
        super(PloneAppContenttypesRobot, self).tearDownPloneSite(portal)


try:
    pkg_resources.get_distribution('Products.ATContentTypes')
    import Products.ATContentTypes
    TEST_MIGRATION = True
except pkg_resources.DistributionNotFound:
    TEST_MIGRATION = False


class PloneAppContenttypesMigration(PloneSandboxLayer):
    """ A setup that installs the old default AT-Types to migrate them to
    Dexterity. The profile of pac is not only in the individual tests.
    """

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        if not TEST_MIGRATION:
            return

        # prepare installing Products.ATContentTypes
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
        self.loadZCML(package=plone.app.contenttypes)
        import plone.app.referenceablebehavior
        self.loadZCML(package=plone.app.referenceablebehavior)

    def setUpPloneSite(self, portal):
        if not TEST_MIGRATION:
            return

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

    def tearDownPloneSite(self, portal):
        if not TEST_MIGRATION:
            return

        applyProfile(portal, 'plone.app.contenttypes:uninstall')

    def tearDownZope(self, app):
        if not TEST_MIGRATION:
            return

        try:
            pkg_resources.get_distribution('plone.app.collection')
            z2.uninstallProduct(app, 'plone.app.collection')
        except pkg_resources.DistributionNotFound:
            pass
        z2.uninstallProduct(app, 'plone.app.blob')
        z2.uninstallProduct(app, 'Products.ATContentTypes')
        z2.uninstallProduct(app, 'Products.Archetypes')


PLONE_APP_CONTENTTYPES_FIXTURE = PloneAppContenttypes()
PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_CONTENTTYPES_FIXTURE,),
    name='PloneAppContenttypes:Integration'
)
PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_CONTENTTYPES_FIXTURE,),
    name='PloneAppContenttypes:Functional'
)
PLONE_APP_CONTENTTYPES_ROBOT_FIXTURE = PloneAppContenttypesRobot()
PLONE_APP_CONTENTTYPES_ROBOT_TESTING = FunctionalTesting(
    bases=(
        PLONE_APP_CONTENTTYPES_ROBOT_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='PloneAppContenttypes:Robot'
)
PLONE_APP_CONTENTTYPES_MIGRATION_FIXTURE = PloneAppContenttypesMigration()
PLONE_APP_CONTENTTYPES_MIGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_CONTENTTYPES_MIGRATION_FIXTURE,),
    name='PloneAppContenttypes:Migration'
)
PLONE_APP_CONTENTTYPES_MIGRATION_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_CONTENTTYPES_MIGRATION_FIXTURE,),
    name='PloneAppContenttypes:Migration_Functional'
)
