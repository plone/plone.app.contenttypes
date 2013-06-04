# -*- coding: utf-8 -*-
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.testing import login

from plone.testing import z2

from zope.configuration import xmlconfig


class PloneAppContenttypesNoInstall(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import plone.app.contenttypes
        xmlconfig.file(
            'configure.zcml',
            plone.app.contenttypes,
            context=configurationContext
        )

    def setUpPloneSite(self, portal):
        portal.acl_users.userFolderAddUser('admin',
                                           'secret',
                                           ['Manager'],
                                           [])
        login(portal, 'admin')
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")
        setRoles(portal, TEST_USER_ID, ['Manager'])

PLONE_APP_CONTENTTYPES_NO_INSTALL_FIXTURE = PloneAppContenttypesNoInstall()
PLONE_APP_CONTENTTYPES_NO_INSTALL_ROBOT_TESTING = FunctionalTesting(
    bases=(PLONE_APP_CONTENTTYPES_NO_INSTALL_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PloneAppContenttypesNoInstall:Robot"
)


class PloneAppContenttypes(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_NO_INSTALL_FIXTURE,)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plone.app.contenttypes:default')
        portal.invokeFactory(
            "Folder",
            id="robot-test-folder",
            title=u"Test Folder"
        )


PLONE_APP_CONTENTTYPES_FIXTURE = PloneAppContenttypes()
PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_CONTENTTYPES_FIXTURE,),
    name="PloneAppContenttypes:Integration"
)
PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_CONTENTTYPES_FIXTURE,),
    name="PloneAppContenttypes:Functional"
)
PLONE_APP_CONTENTTYPES_ROBOT_TESTING = FunctionalTesting(
    bases=(PLONE_APP_CONTENTTYPES_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PloneAppContenttypes:Robot"
)
